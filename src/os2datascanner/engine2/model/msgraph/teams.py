from ..core import Handle, Source, Resource
from .utilities import MSGraphSource, ignore_responses


class MSGraphChatSource(MSGraphSource):
    """
    Engine2 MSGraphSource implementation for MS Teams Chat
    """

    type_label = "msgraph-chat"

    def _list_chats(self, source_manager):
        return source_manager.open(self).get("chats")

    def handles(self, sm):
        for chat in self._list_chats(sm)["value"]:
            chat_id = chat[""]

            with ignore_responses(404):
                any_messages = sm.open(self).get(f"chats/{chat_id}/messages")
                if any_messages["value"]:
                    yield MSGraphChatHandle(self, chat_id)

    @staticmethod
    @Source.json_handler(type_label)
    def from_json_object(obj):
        return MSGraphChatSource(
            client_id=obj["client_id"],
            tenant_id=obj["tenant_id"],
            client_secret=obj["client_secret"],
        )


class MSGraphChatResource(Resource):
    """
    Engine2 Resource implementation for MS Teams Chat
    """

    def check(self) -> bool:
        response = self._get_cookie().get_raw(f"chats/{self.handle.relative_path}/messages")
        return response.status_code not in (
            404,
            410,
        )


@Handle.stock_json_handler("msgraph-chat")
class MSGraphChatHandle(Handle):
    """
    Engine2 Handle implementation for MS Teams Chat
    """

    type_label = "msgraph-chat"
    resource_type = MSGraphChatResource
    eq_properties = Handle.BASE_PROPERTIES

    @property
    def presentation(self):
        return self.relative_path

    def censor(self):
        return MSGraphChatHandle(self.source.censor(), self.relative_path)
