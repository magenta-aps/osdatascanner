from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    # As_asgi instantiates an instance for each user-connection, similar to as_view()
    re_path(r'ws/chat/(?P<room_name>\w+)/$', consumers.ChatConsumer.as_asgi()),
]
