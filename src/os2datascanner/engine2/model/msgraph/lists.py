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

    eq_properties = MSGraphSource.eq_properties

    def __init__(self, client_id, tenant_id, client_secret):
        super().__init__(client_id, tenant_id, client_secret)

    def _make_handle(self, obj, site_id):
        owner_name = None
        if "lastModified" in obj:
            owner_name = obj["lastModifiedBy"]["user"]["displayName"]
        else:
            owner_name = obj["createdBy"]["user"]["displayName"]
        return MSGraphListHandle(self, obj["id"], obj["name"], owner_name, site_id)

    def handles(self, sm):  # noqa
        with warn_on_httperror("SharePoint lists check"):
            sites = sm.open(self).paginated_get(
                "sites/getAllSites?$filter=isPersonalSite ne true")

            for site in sites:
                site_id = site.get("id").split(",")[1]
                lists = sm.open(self).paginated_get(
                    f"sites/{site_id}/lists")

                for sp_list in lists:
                    template = sp_list.get("list").get("template")
                    # Is there a better way to filter off documentLibraries and catalogs?
                    if template != "documentLibrary" and "_catalog" not in sp_list.get("webUrl"):
                        yield self._make_handle(sp_list, site_id)

    def censor(self):
        return type(self)(None, self._tenant_id, None)

    def to_json_object(self):
        return dict(
            **super().to_json_object()
        )

    @staticmethod
    @Source.json_handler(type_label)
    def from_json_object(obj):
        return MSGraphListsSource(
                client_id=obj["client_id"],
                tenant_id=obj["tenant_id"],
                client_secret=obj["client_secret"])


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
    type_label = "msgraph-list"
    resource_type = MSGraphListResource
    eq_properties = Handle.eq_properties + ("_list_name",)

    def __init__(self, source, path, list_name, owner_name, site_id):
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
        # Sharepoint is more telling but Office 365 is more consistent for our
        # user space... PepoThink
        return "Sharepoint"

    def guess_type(self):
        return DUMMY_MIME

    @property
    def sort_key(self):
        return f"{self._list_name}"

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

    def handles(self, sm):
        gc: MSGraphSource.GraphCaller = sm.open(self)
        list_items = gc.get(
            f"sites/{self.handle._site_id}/lists/{self.handle.relative_path}/items").json()["value"]
        for item in list_items:
            yield MSGraphListItemHandle(
                self,
                self.handle.relative_path,
                self.handle._site_id, item["id"], item["webUrl"])


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
            self._get_cookie().get(self.make_path())
            return True
        except HTTPError as ex:
            if ex.response.status_code in (404, 410,):
                return False
            raise

    def get_metadata(self):
        if not self._metadata:
            self._metadata = self._get_cookie().get(self.make_path()).json()
        return self._metadata

    def get_last_modified(self):
        timestamp = self.get_metadata().get("lastModifiedDateTime")
        return isoparse(timestamp) if timestamp else None

    def get_size(self):
        return 1

    def compute_type(self):
        return "text/plain"

    def make_path(self):
        return (
            f"sites/{self.handle._site_id}/lists/{self.handle.relative_path}/items/"
            f"{self.handle._item_id}"
        )

    @contextmanager
    def make_stream(self):
        response = self._get_cookie().get(self.make_path())
        with BytesIO(response.content) as fp:
            yield fp


class MSGraphListItemHandle(Handle):
    type_label = "msgraph-list-item"
    resource_type = MSGraphListItemResource

    def __init__(self, source, path, site_id, item_id, webUrl):
        super().__init__(source, path)
        self._site_id = site_id
        self._item_id = item_id
        self._webUrl = webUrl

    @property
    def presentation_name(self):
        return self.source.handle._list_name

    @property
    def presentation_place(self):
        return f"{self.relative_path}/{self.source.handle._list_name}"

    @property
    def presentation_url(self):
        # This links to list, find way to link to item??
        return self._webUrl.split(f"/{self._item_id}")[0]

    @property
    def sort_key(self):
        return self.source.handle.sort_key + (f"/{self._item_id}")

    def guess_type(self):
        return "text/plain"

    def to_json_object(self):
        return dict(
            **super().to_json_object(),
            site_id=self._site_id,
            item_id=self._item_id,
            webUrl=self._webUrl
        )

    @staticmethod
    @Handle.json_handler(type_label)
    def from_json_object(obj):
        return MSGraphListItemHandle(
            Source.from_json_object(obj["source"]),
            path=obj["path"],
            site_id=obj.get("site_id"),
            item_id=obj.get("item_id"),
            webUrl=obj.get("webUrl")
        )
