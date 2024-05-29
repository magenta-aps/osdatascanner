from io import BytesIO
from contextlib import contextmanager
from dateutil.parser import isoparse
from requests import HTTPError

from ..core import Handle, Source, Resource, FileResource
from ..derived.derived import DerivedSource
from .utilities import MSGraphSource, warn_on_httperror


class MSGraphFilesSource(MSGraphSource):
    type_label = "msgraph-files"

    eq_properties = MSGraphSource.eq_properties + ("_userlist",)

    def __init__(self, client_id, tenant_id, client_secret,
                 site_drives=True, user_drives=True, userlist=None):
        super().__init__(client_id, tenant_id, client_secret)
        self._site_drives = site_drives
        self._user_drives = user_drives
        self._userlist = userlist

    def _make_drive_handle(self, obj):
        owner_name = None
        if "owner" in obj:
            if "user" in obj["owner"]:
                owner_name = obj["owner"]["user"]["displayName"]
            elif "group" in obj:
                owner_name = obj["owner"]["group"]["displayName"]
        return MSGraphDriveHandle(self, obj["id"], obj["name"], owner_name)

    def handles(self, sm):  # noqa
        if self._site_drives:
            with warn_on_httperror("SharePoint drive check"):
                # Get all sites possible, but exclude personal ones, as they usually
                # will lead us to users 'personal' OneDrive.
                sites = sm.open(self).paginated_get(
                    "sites/getAllSites?$filter=isPersonalSite ne true")

                for site in sites:
                    # For some reason, this returns id key as 3 comma seperated values ...
                    # tenant, site id, some other id.
                    site_id = site.get("id").split(",")[1]
                    site_w_drive = sm.open(self).get(
                        f"sites/{site_id}?$select=*,drive&$expand=drive").json()

                    # Grab the "drive" found navigating this site
                    drive = site_w_drive.get("drive")

                    yield self._make_drive_handle(drive)

        if self._user_drives:
            if self._userlist is None:
                for user in self._list_users(sm):
                    pn = user["userPrincipalName"]
                    with warn_on_httperror(f"drive check for {pn}"):
                        drive = sm.open(self).get("users/{0}/drive".format(pn)).json()
                        yield self._make_drive_handle(drive)

            else:
                for pn in self._userlist:
                    with warn_on_httperror(f"drive check for {pn}"):
                        drive = sm.open(self).get(f"users/{pn}/drive").json()
                        yield self._make_drive_handle(drive)

    def to_json_object(self):
        return dict(
            **super().to_json_object(),
            site_drives=self._site_drives,
            user_drives=self._user_drives,
            userlist=list(self._userlist) if self._userlist is not None else None
        )

    @staticmethod
    @Source.json_handler(type_label)
    def from_json_object(obj):
        userlist = obj.get("userlist")
        return MSGraphFilesSource(
                client_id=obj["client_id"],
                tenant_id=obj["tenant_id"],
                client_secret=obj["client_secret"],
                site_drives=obj["site_drives"],
                user_drives=obj["user_drives"],
                userlist=frozenset(userlist) if userlist is not None else None)


DUMMY_MIME = "application/vnd.os2.datascanner.graphdrive"


class MSGraphDriveResource(Resource):
    def check(self) -> bool:
        try:
            self._get_cookie().get("drives/{0}?$select=id".format(self.handle.relative_path))
            return True
        except HTTPError as ex:
            if ex.response.status_code in (404, 410,):
                return False
            raise

    def compute_type(self):
        return DUMMY_MIME


class MSGraphDriveHandle(Handle):
    type_label = "msgraph-drive"
    resource_type = MSGraphDriveResource
    eq_properties = Handle.eq_properties + ("_user_account",)

    def __init__(self, source, path, folder_name, owner_name, *, user_account=None):
        super().__init__(source, path)
        self._folder_name = folder_name
        self._owner_name = owner_name
        self._user_account = user_account

    @property
    def presentation_name(self):
        if self._user_account:
            return f"{self._user_account}'s files"
        elif self._owner_name:
            return "\"{0}\" (owned by {1})".format(
                    self._folder_name, self._owner_name)
        else:
            return "\"{0}\"".format(self._folder_name)

    @property
    def presentation_place(self):
        return "Office 365"

    def guess_type(self):
        return DUMMY_MIME

    def to_json_object(self):
        return super().to_json_object() | {
            "folder_name": self._folder_name,
            "owner_name": self._owner_name,
            "user_account": self._user_account,
        }

    @staticmethod
    @Handle.json_handler(type_label)
    def from_json_object(obj):
        return MSGraphDriveHandle(
                Source.from_json_object(obj["source"]), obj["path"],
                obj["folder_name"], obj["owner_name"],
                user_account=obj.get("user_account"))


@Source.mime_handler(DUMMY_MIME)
class MSGraphDriveSource(DerivedSource):
    type_label = "msgraph-drive"
    derived_from = MSGraphDriveHandle

    def _generate_state(self, sm):
        yield sm.open(self.handle.source)

    @property
    def _drive_path(self):
        if drive_id := self.handle.relative_path:
            return f"drives/{drive_id}"
        elif user_principal_name := self.handle._user_account:
            return f"users/{user_principal_name}/drive"
        else:
            raise ValueError("Object didn't contain any driveId or UPN!:"
                             f" {self.to_json_object()}")

    def handles(self, sm):
        gc: MSGraphSource.GraphCaller = sm.open(self)

        def _explore_folder(
                components, folder, parent_weblink=None, is_root=False):
            for obj in folder:
                name = obj["name"]
                web_url = obj.get("webUrl", None)
                if is_root:
                    # Microsoft appears to have changed the default home page
                    # of OneDrive from an actual list of files (which we want)
                    # to some sort of fuzzy recent overview (which we don't)
                    # without updating webUrl accordingly. Groan; attempt to
                    # correct for that by requesting the file list view
                    web_url += "?view=0"
                here = components + ([name] if not is_root else [])
                if "file" in obj:
                    yield MSGraphFileHandle(
                            self, "/".join(here),
                            weblink=web_url, parent_weblink=parent_weblink)
                elif "folder" in obj:
                    folder_id: str = obj["id"]
                    subfolder = gc.get(
                            f"{self._drive_path}/items/"
                            f"{folder_id}/children").json()
                    yield from _explore_folder(
                            here, subfolder["value"], parent_weblink=web_url)
        root = [gc.get(f"{self._drive_path}/root").json()]
        yield from _explore_folder([], root, is_root=True)


class MSGraphFileResource(FileResource):
    def __init__(self, sm, handle):
        super().__init__(sm, handle)
        self._metadata = None

    def _generate_metadata(self):
        msgraph_metadata = self.get_file_metadata()
        yield "msgraph-owner-account", msgraph_metadata["createdBy"]["user"]["email"]
        yield "msgraph-last-modified-by", msgraph_metadata["lastModifiedBy"]["user"]["email"]
        yield "msgraph-last-modified-date-time", msgraph_metadata["lastModifiedDateTime"]
        yield from super()._generate_metadata()

    def check(self) -> bool:
        try:
            self._get_cookie().get(self.make_object_path())
            return True
        except HTTPError as ex:
            if ex.response.status_code in (404, 410,):
                return False
            raise

    def make_object_path(self):
        drive_path: str = self.handle.source._drive_path
        return f"{drive_path}/root:/{self.handle.relative_path}"

    def get_file_metadata(self):
        if not self._metadata:
            self._metadata = self._get_cookie().get(self.make_object_path()).json()
        return self._metadata

    def get_last_modified(self):
        timestamp = self.get_file_metadata().get("lastModifiedDateTime")
        return isoparse(timestamp) if timestamp else None

    def get_size(self):
        return self.get_file_metadata()["size"]

    @contextmanager
    def make_stream(self):
        response = self._get_cookie().get(
                self.make_object_path() + ":/content")
        with BytesIO(response.content) as fp:
            yield fp


class MSGraphFileHandle(Handle):
    type_label = "msgraph-drive-file"
    resource_type = MSGraphFileResource

    def __init__(self, source, path, weblink=None, parent_weblink=None):
        super().__init__(source, path)
        self._weblink = weblink
        self._parent_weblink = parent_weblink

    @property
    def presentation_name(self):
        return self.name

    @property
    def presentation_url(self):
        return self._weblink

    @property
    def container_url(self):
        return self._parent_weblink

    @property
    def presentation_place(self):
        folder = self.relative_path.removesuffix(self.name)
        parent = str(self.source.handle)
        if folder:
            return f"{folder} (in {parent})"
        else:
            return parent

    def to_json_object(self):
        return dict(
            **super().to_json_object(),
            weblink=self._weblink,
            parent_weblink=self._parent_weblink)

    @staticmethod
    @Handle.json_handler(type_label)
    def from_json_object(obj):
        return MSGraphFileHandle(
            Source.from_json_object(obj["source"]),
            obj["path"], obj.get("weblink"),
            obj.get("parent_weblink"))
