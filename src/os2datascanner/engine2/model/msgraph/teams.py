from io import BytesIO
from contextlib import contextmanager

from ...conversions.utilities.results import SingleResult
from ... import settings as engine2_settings
from ..core import Handle, Source, Resource, FileResource
from ..derived.derived import DerivedSource
from ..utilities import NamedTemporaryResource
from .utilities import MSGraphSource, ignore_responses


class MSGraphTeamsSource(MSGraphSource):
    """
    Engine2 MSGraphSource implementation for MS Teams Chat
    """

    type_label = "msgraph-chat"

    def __init__(self, client_id, tenant_id, client_secret, userlist=None):
        super().__init__(client_id, tenant_id, client_secret)
        self._userlist = userlist or None

    def handles(self, sm):  # noqa
        if self._userlist is None:
            for user in self._list_users(sm)["value"]:
                pn = user["userPrincipalName"]

                with ignore_responses(404):
                    any_messages = sm.open(self).get(
                        "users/{0}/chats?$select=id&$top=1".format(pn))
                    if not any_messages["value"]:
                        continue

                    yield MSGraphTeamsAccountHandle(self, pn)
        else:
            for pn in self._userlist:
                with ignore_responses(404):
                    any_messages = sm.open(self).get(
                        "users/{0}/chats?$select=id&$top=1".format(pn))
                    if any_messages["value"]:
                        yield MSGraphTeamsAccountHandle(self, pn)

    def to_json_object(self):
        return dict(
                **super().to_json_object(),
                userlist=list(self._userlist) if self._userlist else None)

    @staticmethod
    @Source.json_handler(type_label)
    def from_json_object(obj):
        userlist = obj.get("userlist")
        return MSGraphTeamsSource(
            client_id=obj["client_id"],
            tenant_id=obj["tenant_id"],
            client_secret=obj["client_secret"],
            userlist=frozenset(userlist) if userlist else None)


DUMMY_MIME = "application/vnd.os2.datascanner.graphteamsaccount"


class MSGraphTeamsAccountResource(Resource):
    def check(self) -> bool:
        response = self._get_cookie().get_raw(
            "users/{0}/chats?$select=id&$top=1".format(
                self.handle.relative_path))
        return response.status_code not in (404, 410,)

    def compute_type(self):
        return DUMMY_MIME


@Handle.stock_json_handler("msgraph-teams-account")
class MSGraphTeamsAccountHandle(Handle):
    type_label = "msgraph-teams-account"
    resource_type = MSGraphTeamsAccountResource

    @property
    def presentation(self):
        return self.relative_path

    def guess_type(self):
        return DUMMY_MIME

    def censor(self):
        return MSGraphTeamsAccountHandle(
            self.source.censor(), self.relative_path)


@Source.mime_handler(DUMMY_MIME)
class MSGraphTeamsAccountSource(DerivedSource):
    type_label = "msgraph-teams-account"

    def _generate_state(self, sm):
        yield sm.open(self.handle.source)

    def handles(self, sm):
        pn = self.handle.relative_path
        result = sm.open(self).get(
            "users/{}/chats/getAllMessages?$select=id,subject,webUrl,chatId&$top={}".format(
                pn, engine2_settings.model["msgraph"]["page_size"]))

        yield from (self._wrap(msg) for msg in result["value"])

        while '@odata.nextLink' in result:
            result = sm.open(self).follow_next_link(result["@odata.nextLink"])
            yield from (self._wrap(msg) for msg in result["value"])

    def _wrap(self, msg):
        return MSGraphTeamsMessageHandle(
            self, msg["id"], msg["subject"], msg["webUrl"], msg["chatId"])


class MSGraphTeamsMessageResource(FileResource):
    def __init__(self, handle, sm):
        super().__init__(handle, sm)
        self._message = None
        self._body = None

    def _generate_metadata(self):
        yield "email-account", self.handle.source.handle.relative_path
        yield from super()._generate_metadata()

    def _get_body(self):
        if not self._body:
            self._body = self._get_cookie().get(
                    self.make_object_path() + "?$select=body")
        return self._body

    def check(self) -> bool:
        response = self._get_cookie().get_raw(
                self.make_object_path() + "?$select=id")
        return response.status_code not in (404, 410,)

    def make_object_path(self):
        return "users/{0}/chats/{1}/messages/{2}".format(
            self.handle.source.handle.relative_path,
            self.handle.chatId,
            self.handle.relative_path)

    def get_event_metadata(self):
        if not self._event:
            self._event = self._get_cookie().get(
                self.make_object_path() + "?$select=lastModifiedDateTime")
        return self._event

    @contextmanager
    def make_path(self):
        with NamedTemporaryResource(self.handle.name) as ntr:
            with ntr.open("wb") as res:
                with self.make_stream() as s:
                    res.write(s.read())
            yield ntr.get_path()

    @contextmanager
    def make_stream(self):
        with BytesIO(self._get_body()["body"]["content"].encode()) as fp:
            yield fp

    def compute_type(self):
        return ("text/html"
                if self._get_body()["body"]["contentType"] == "html"
                else "text/plain")

    def get_size(self):
        return SingleResult(None, 'size', 1024)


class MSGraphTeamsMessageHandle(Handle):
    type_label = "msgraph-teams-message"
    resource_type = MSGraphTeamsMessageResource
    eq_properties = Handle.BASE_PROPERTIES

    def __init__(self, source, path, message_subject, webUrl, chatId):
        super().__init__(source, path)
        self._message_subject = message_subject
        self._webUrl = webUrl
        self.chatId = chatId

    @property
    def presentation(self):
        return f'Account {self.source.handle.relative_path}'

    @property
    def presentation_name(self):
        return self._message_subject

    @property
    def presentation_url(self):
        return self._webUrl

    def censor(self):
        return MSGraphTeamsMessageHandle(
            self.source.censor(), self.relative_path,
            self._message_subject, self._webUrl, self.chatId)

    def to_json_object(self):
        return dict(
            **super().to_json_object(),
            message_subject=self._message_subject,
            webUrl=self._webUrl,
        )

    @staticmethod
    @Handle.json_handler(type_label)
    def from_json_object(obj):
        return MSGraphTeamsMessageHandle(
            Source.from_json_object(obj["source"]), obj["path"],
            obj["message_subject"], obj["webUrl"], obj["chatId"])
