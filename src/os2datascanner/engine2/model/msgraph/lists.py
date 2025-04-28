from io import BytesIO
from contextlib import contextmanager
from dateutil.parser import isoparse
from requests import HTTPError

from ...utilities.i18n import gettext as _
from ..core import Handle, Source, Resource
from ..derived.derived import DerivedSource
from .utilities import MSGraphSource, warn_on_httperror


class MSGraphListsSource(MSGraphSource):
    type_label = "msgraph-lists"

    eq_properties = MSGraphSource.eq_properties + ("_sitelist",)

    def __init__(self, client_id, tenant_id, client_secret, sitelist=None):
        super().__init__(client_id, tenant_id, client_secret)
        self._sitelist = sitelist

    def _make_handle(self, obj, site_id):
        owner_name = None
        print(obj)
        if "lastModified" in obj:
            owner_name = obj["lastModifiedBy"]["user"]["displayName"]
        else:
            owner_name = obj["createdBy"]["user"]["displayName"]
        return MSGraphListHandle(self, obj["id"], obj["name"], owner_name, site_id)

    def handles(self, sm):  # noqa
        with warn_on_httperror("SharePoint lists check"):
            # sites = sm.open(self).paginated_get(
            #     "sites/getAllSites?$filter=isPersonalSite ne true")
            sites = [{
              "@odata.context": "https://graph.microsoft.com/v1.0/$metadata#sites/$entity",
              "createdDateTime": "2022-03-07T12:43:27.34Z",
              "description": "This is a MS Graph API Test environment.",
              "id": "magenta43dk.sharepoint.com,095ba61f-7f12-4894-b43a-7c40ee13dc9e,502681d3-5b32-48f3-926d-164a4f52b4eb",  # noqa
              "lastModifiedDateTime": "2025-04-24T12:40:50Z",
              "name": "GraphAPITest",
              "webUrl": "https://magenta43dk.sharepoint.com/sites/GraphAPITest",
              "displayName": "GraphAPITest",
              "root": {},
              "siteCollection": {
                "hostname": "magenta43dk.sharepoint.com"
              }
            }]

            # TODO: fix this whole ordeal

            for site in sites:
                site_id = site.get("id").split(",")[1]
                lists = sm.open(self).paginated_get(
                    f"sites/{site_id}/lists")
                for list in lists:
                    template = list.get("list").get("template")
                    if template != "documentLibrary" and "_catalog" not in list.get("webUrl"):
                        yield self._make_handle(list, site_id)

    def to_json_object(self):
        return dict(
            **super().to_json_object(),
            sitelist=list(self._sitelist) if self._sitelist is not None else None
        )

    @staticmethod
    @Source.json_handler(type_label)
    def from_json_object(obj):
        sitelist = obj.get("sitelist")
        return MSGraphListsSource(
                client_id=obj["client_id"],
                tenant_id=obj["tenant_id"],
                client_secret=obj["client_secret"],
                sitelist=frozenset(sitelist) if sitelist is not None else None)


DUMMY_MIME = "application/vnd.os2.datascanner.graphlist"


class MSGraphListResource(Resource):
    def check(self) -> bool:
        try:
            self._get_cookie().get("sites/lists/{0}?$select=id".format(self.handle.relative_path))
            return True
        except HTTPError as ex:
            if ex.response.status_code in (404, 410,):
                return False
            raise

    def compute_type(self):
        return DUMMY_MIME


class MSGraphListHandle(Handle):
    type_label = "msgraph-lists"
    resource_type = MSGraphListResource
    eq_properties = Handle.eq_properties + ("_list_name",)

    def __init__(self, source, path, list_name, owner_name, site_id):
        print(source)
        super().__init__(source, path)
        self._list_name = list_name
        self._owner_name = owner_name
        self._site_id = site_id

    @property
    def presentation_name(self):
        if self._list_name:
            return _("List: {list_name}").format(
                    list_name=self._list_name)
        elif self._owner_name:
            return _("\"{list_name}\" (owned by {owner})").format(
                    list_name=self._list_name, owner=self._owner_name)
        else:
            return "\"{0}\"".format(self._list_name)

    @property
    def presentation_place(self):
        return "Sharepoint"

    def guess_type(self):
        return DUMMY_MIME

    def to_json_object(self):
        return super().to_json_object() | {
            "list_name": self._list_name,
            "owner_name": self._owner_name,
            "site_id": self._site_id
        }

    @staticmethod
    @Handle.json_handler(type_label)
    def from_json_object(obj):
        return MSGraphListHandle(
                Source.from_json_object(obj["source"]), obj["path"],
                obj["list_name"], obj["owner_name"], obj["site_id"])


@Source.mime_handler(DUMMY_MIME)
class MSGraphListSource(DerivedSource):
    type_label = "msgraph-list"
    derived_from = MSGraphListHandle

    def _generate_state(self, sm):
        yield sm.open(self.handle.source)

    @property
    def _list_path(self):
        if list_id := self.handle.relative_path:
            return f"sites/{self.handle._site_id}/lists/{list_id}"
        else:
            raise ValueError("Object didn't contain any list_id or UPN!:"
                             f" {self.to_json_object()}")

    def handles(self, sm):
        gc: MSGraphSource.GraphCaller = sm.open(self)
        list_items = gc.get(f"{self._list_path}/items").json()["value"]
        for item in list_items:
            yield MSGraphListItemHandle(
                self.handle.source,
                self.handle.relative_path,
                self.handle._site_id, item["id"])


class MSGraphListItemResource(Resource):
    def __init__(self, sm, handle):
        super().__init__(sm, handle)
        self._metadata = None

    def _generate_metadata(self):
        msgraph_metadata = self.get_metadata()
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

    def get_metadata(self):
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


class MSGraphListItemHandle(Handle):
    type_label = "msgraph-list-item"
    resource_type = MSGraphListItemResource

    def __init__(self, source, path, site_id, weblink):
        super().__init__(source, path)
        self._site_id = site_id
        self._weblink = weblink

    @property
    def presentation_place(self):
        return self._site_id

    @property
    def presentation_name(self):
        return "presentation_name"

    @property
    def presentation_url(self):
        return self._weblink

    @property
    def sort_key(self):
        return self.source.handle.sort_key + (f"{self._site_id}")

    def guess_type(self):
        return DUMMY_MIME

    @property
    def scan_lists(self):
        return True

    def to_json_object(self):
        return dict(
            **super().to_json_object(),
            site_id=self._site_id,
            weblink=self._weblink
        )

    @staticmethod
    @Handle.json_handler(type_label)
    def from_json_object(obj):
        return MSGraphListItemHandle(
            source=obj["source"],
            path=obj["path"],
            site_id=obj.get("site_id"),
            weblink=obj.get("weblink")
        )
