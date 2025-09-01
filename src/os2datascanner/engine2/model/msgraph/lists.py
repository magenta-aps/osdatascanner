import csv
from io import BytesIO, StringIO
from urllib.parse import unquote
from contextlib import contextmanager
from dateutil.parser import isoparse
from requests import HTTPError
from datetime import datetime, timezone

from os2datascanner.engine2.rules.rule import Rule
from os2datascanner.engine2.rules.utilities.analysis import compute_mss

from ..core import Handle, Source, Resource, FileResource
from ..derived.derived import DerivedSource
from .utilities import MSGraphSource, warn_on_httperror
from ...utilities.i18n import gettext as _


class MSGraphListsSource(MSGraphSource):
    type_label = "msgraph-lists"

    eq_properties = MSGraphSource.eq_properties

    def __init__(self, client_id, tenant_id, client_secret, sites=None, scan_descriptions=False):
        super().__init__(client_id, tenant_id, client_secret)
        self.sites = sites
        self.scan_descriptions = scan_descriptions

    def handles(self, sm, *, rule: Rule | None = None):  # noqa
        cutoff = None

        for essential_rule in compute_mss(rule):
            # (we can't do isinstance() here without making a circular
            # dependency)
            if essential_rule.type_label == "last-modified":
                after = essential_rule.after
                cutoff = (after if not cutoff else max(cutoff, after))

        if self.sites:
            with warn_on_httperror("SharePoint selected lists check"):
                for site in self.sites:
                    site_id = site['uuid']
                    yield from self._process_site(sm, site_id, cutoff)
        else:
            with warn_on_httperror("SharePoint all lists check"):
                sites = sm.open(self).paginated_get(
                    "sites/getAllSites?$filter=isPersonalSite ne true")
                for site in sites:
                    site_id = site.get("id").split(",")[1]
                    yield from self._process_site(sm, site_id, cutoff)

    def _process_site(self, sm, site_id, cutoff):
        query = f"sites/{site_id}/lists"
        lists = sm.open(self).paginated_get(query)

        # Filtering off lists with no changes when doing standard scans.
        # MSGraph does not allow for filtering on lastModifiedDateTime
        # and filtering solely on the list item level is significantly slower.
        if cutoff:
            ts = cutoff.astimezone(timezone.utc)
            lists = filter(lambda x: datetime.strptime(
                x['lastModifiedDateTime'], "%Y-%m-%dT%H:%M:%SZ").
                    replace(tzinfo=timezone.utc) > ts, lists)

        for sp_list in lists:
            match sp_list:
                case {"list": {"template": "documentLibrary"}}:
                    # This is a SharePoint drive in disguise. Ignore it
                    continue
                case {"webUrl": u} if "/_catalogs" in u:
                    # Catalog lists take up a lot of space and contain
                    # blank templates. Ignore them
                    continue
                case {"id": id, "name": name}:
                    yield MSGraphListHandle(self, id, name, site_id)

    def censor(self):
        return type(self)(None, self._tenant_id, None, self.sites)

    @staticmethod
    @Source.json_handler(type_label)
    def from_json_object(obj):
        return MSGraphListsSource(
                client_id=obj["client_id"],
                tenant_id=obj["tenant_id"],
                client_secret=obj["client_secret"],
                sites=obj.get("sites"),
                scan_descriptions=obj.get("scan_descriptions")
        )

    def to_json_object(self):
        return dict(
            **super().to_json_object(),
            sites=self.sites,
            scan_descriptions=self.scan_descriptions
        )


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

    def __init__(self, source, path, list_name, site_id):
        super().__init__(source, path)
        self._list_name = list_name
        self._site_id = site_id

    @property
    def presentation_name(self):
        return self._list_name

    @property
    def presentation_place(self):
        return "SharePoint"

    def guess_type(self):
        return DUMMY_MIME

    @property
    def sort_key(self):
        return f"{self._list_name}"

    def to_json_object(self):
        return super().to_json_object() | {
            "list_name": self._list_name,
            "site_id": self._site_id
        }

    @staticmethod
    @Handle.json_handler(type_label)
    def from_json_object(obj):
        return MSGraphListHandle(
                Source.from_json_object(obj["source"]), obj["path"],
                obj["list_name"], obj["site_id"])


@Source.mime_handler(DUMMY_MIME)
class MSGraphListSource(DerivedSource):
    type_label = "msgraph-list"
    derived_from = MSGraphListHandle

    def _generate_state(self, sm):
        yield sm.open(self.handle.source)

    def _build_query(
            self,
            query: str,
            cutoff: datetime | None = None):

        filters = []

        if cutoff:
            # Microsoft Graph requires all timestamps to be in UTC and doesn't
            # support any way of saying that other than "Z".
            ts = cutoff.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
            fs = f"fields/Modified gt '{ts}'"
            filters.append(fs)

        if filters:
            query += f"$filter={' and '.join(filters)}&$expand=fields"
        else:
            query += "$expand=fields"
        return query

    def handles(self, sm, *, rule: Rule | None = None):
        gc: MSGraphSource.GraphCaller = sm.open(self)

        query = f"sites/{self.handle._site_id}/lists/{self.handle.relative_path}/items?"
        cutoff = None

        for essential_rule in compute_mss(rule):
            # (we can't do isinstance() here without making a circular
            # dependency)
            if essential_rule.type_label == "last-modified":
                after = essential_rule.after
                cutoff = (after if not cutoff else max(cutoff, after))

        query = self._build_query(cutoff=cutoff, query=query)

        for item in gc.paginated_get(query):
            rel_path = f"{self.handle.relative_path}/items/{item['id']}"
            yield MSGraphListItemHandle(
                self,
                rel_path,
                self.handle._site_id, item["id"], item["webUrl"], item["fields"].get("LinkTitle", ))

        if self.handle.source.scan_descriptions:
            list_weburl = gc.get(
                f"sites/{self.handle._site_id}/lists/{self.handle.relative_path}").json()['webUrl']
            yield MSGraphListDescriptionHandle(self,
                                               f"{self.handle.relative_path}",
                                               list_weburl
                                               )


class MSGraphListItemResource(FileResource):
    def __init__(self, sm, handle):
        super().__init__(sm, handle)
        self._metadata = None

    def _generate_metadata(self):
        msgraph_metadata = self.get_listitem_metadata()
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

    def get_listitem_metadata(self):
        if not self._metadata:
            query = "?$select=id,createdBy,lastModifiedBy,lastModifiedDateTime"
            self._metadata = self._get_cookie().get(self.make_path()+query).json()
        return self._metadata

    def get_last_modified(self):
        timestamp = self.get_listitem_metadata().get("lastModifiedDateTime")

        return isoparse(timestamp) if timestamp else None

    def get_size(self):
        return 1

    def compute_type(self):
        return "text/csv"

    def make_path(self):
        return f"sites/{self.handle.source.handle._site_id}/lists/{self.handle.relative_path}"

    @staticmethod
    def json_to_csv_bytes(jsonObj):
        output = StringIO()

        # Define columns to exclude (system/metadata columns)?
        exclude_columns = {
            '@odata.etag', 'id', 'ContentType', 'Modified', 'Created',
            'AuthorLookupId', 'EditorLookupId', '_UIVersionString',
            'Attachments', 'Edit', 'LinkTitleNoMenu', 'LinkTitle',
            'ItemChildCount', 'FolderChildCount', '_ComplianceFlags',
            '_ComplianceTag', '_ComplianceTagWrittenTime',
            '_ComplianceTagUserId', 'AppEditorLookupId'
        }

        flattened = {}
        for key, value in jsonObj.items():
            if isinstance(value, dict):
                for nested_key, nested_value in value.items():
                    flattened[f"{key}.{nested_key}"] = nested_value
            elif isinstance(value, list):
                flattened[key] = '; '.join(str(item) for item in value)
            elif isinstance(value, bool):
                flattened[key] = str(value)
            elif value is None:
                flattened[key] = ''
            else:
                flattened[key] = value

        filtered_columns = [col for col in flattened.keys() if col not in exclude_columns]

        writer = csv.DictWriter(
            output,
            fieldnames=filtered_columns,
            extrasaction='ignore',
        )

        writer.writeheader()
        writer.writerow(flattened)

        csv_bytes = output.getvalue().encode('utf-8')
        output.close()
        return csv_bytes

    @contextmanager
    def make_stream(self):
        if isinstance(self.handle, MSGraphListItemHandle):
            response = self._get_cookie().get(self.make_path())
            list_item = response.json()["fields"]
            list_csv = self.json_to_csv_bytes(list_item)

        elif isinstance(self.handle, MSGraphListDescriptionHandle):
            query = self.make_path()+'/columns?$select=displayName,description'
            response = self._get_cookie().get(query).json()

            description = {}
            for desc in response['value']:
                description[desc["displayName"]] = desc["description"]

            list_csv = self.json_to_csv_bytes(description)

        else:
            list_csv = b''

        with BytesIO(list_csv) as fp:
            yield fp


class MSGraphListItemHandle(Handle):
    type_label = "msgraph-list-item"
    resource_type = MSGraphListItemResource

    def __init__(self, source, path, site_id, item_id, webUrl, item_name):
        super().__init__(source, path)
        self._site_id = site_id
        self._item_id = item_id
        self._webUrl = webUrl
        self._item_name = item_name

    @property
    def presentation_name(self):
        if self._item_name:
            return self._item_name
        else:
            return self.source.handle._list_name

    @property
    def site_name(self):
        return unquote(self._webUrl.split("/")[4])

    @property
    def presentation_place(self):
        return _('List "{list_name}" (on site {site_name})').format(
            list_name=self.source.handle._list_name, site_name=self.site_name)

    @property
    def presentation_url(self):
        # The webUrl for items don't seem to work so we'll link to list instead
        return self._webUrl.split(f"/{self._item_id}")[0]

    @property
    def sort_key(self):
        return f"{self.site_name}/{self.source.handle._list_name}/{self._item_id}"

    def guess_type(self):
        return "text/csv"

    def to_json_object(self):
        return dict(
            **super().to_json_object(),
            site_id=self._site_id,
            item_id=self._item_id,
            webUrl=self._webUrl,
            item_name=self._item_name
        )

    @staticmethod
    @Handle.json_handler(type_label)
    def from_json_object(obj):
        return MSGraphListItemHandle(
            Source.from_json_object(obj["source"]),
            path=obj["path"],
            site_id=obj.get("site_id"),
            item_id=obj.get("item_id"),
            webUrl=obj.get("webUrl"),
            item_name=obj.get("item_name")
        )


class MSGraphListDescriptionHandle(Handle):
    type_label = "msgraph-list-description"
    resource_type = MSGraphListItemResource

    def __init__(self, source, path, webUrl):
        super().__init__(source, path)
        self.webUrl = webUrl

    @property
    def presentation_name(self):
        # It would be cool if we could tell the user which field has the description with a result
        return _('Description in list "{list_name}"').format(
             list_name=self.source.handle._list_name)

    @property
    def site_name(self):
        return unquote(self.webUrl.split("/")[4])

    @property
    def presentation_place(self):
        return _('List "{list_name}" (on site {site_name})').format(
            list_name=self.source.handle._list_name, site_name=self.site_name)

    @property
    def presentation_url(self):
        return self.webUrl

    @property
    def sort_key(self):
        return f"{self.site_name}/{self.source.handle._list_name}/description"

    def guess_type(self):
        return "text/csv"

    def to_json_object(self):
        return dict(
            **super().to_json_object(),
            webUrl=self.webUrl
        )

    @staticmethod
    @Handle.json_handler(type_label)
    def from_json_object(obj):
        return MSGraphListDescriptionHandle(
            Source.from_json_object(obj["source"]),
            path=obj["path"],
            webUrl=obj.get("webUrl"),
        )
