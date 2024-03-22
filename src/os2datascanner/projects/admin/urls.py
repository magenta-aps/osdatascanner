"""Admin App URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/

"""
from django.conf import settings
from django.contrib import admin
from django.urls import include, path

_active_apps = settings.INSTALLED_APPS

urlpatterns = [
    path('', include('os2datascanner.projects.admin.adminapp.urls')),
    path('grants/', include('grants.urls')),
    path('core/', include('os2datascanner.projects.admin.core.urls')),
    path('admin/', admin.site.urls),  # Enables admin
]

# Conditionally include urls for relevant active osdatascanner apps:
if 'os2datascanner.projects.admin.organizations' in _active_apps:
    urlpatterns.append(path('organizations/', include('organizations.urls')))
if 'os2datascanner.projects.admin.import_services' in _active_apps:
    urlpatterns.append(path('imports/', include('import_services.urls')))
if (hasattr(settings, "OPTIONAL_APPS") and "debug_toolbar" in settings.OPTIONAL_APPS):
    import debug_toolbar
    urlpatterns.append(path('__debug__/', include(debug_toolbar.urls)))
