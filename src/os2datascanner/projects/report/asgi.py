import os
import django

from channels.http import AsgiHandler
from channels.routing import ProtocolTypeRouter, URLRouter
from os2datascanner.projects.report.reportapp import routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'os2datascanner.projects.report.settings')
django.setup()

from channels.auth import AuthMiddlewareStack

application = ProtocolTypeRouter({
  "http": AsgiHandler,
  "websocket": AuthMiddlewareStack(
    URLRouter(
      routing.websocket_urlpatterns
    )
  ),
})
