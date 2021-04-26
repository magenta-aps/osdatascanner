import os

from channels.auth import AuthMiddlewareStack
from channels.http import AsgiHandler
from channels.routing import ProtocolTypeRouter, URLRouter
from .reportapp import routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'os2datascanner.projects.report.settings"')
django.setup()

application = ProtocolTypeRouter({
  "http": AsgiHandler,
  "websocket": AuthMiddlewareStack(
    URLRouter(
      routing.websocket_urlpatterns
    )
  ),
})
