"""Report App URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/

"""
from django.conf import settings
from django.contrib import admin
from django.urls import include, path

_active_apps = settings.INSTALLED_APPS

urlpatterns = [
    path('', include('os2datascanner.projects.report.reportapp.urls')),
    path('admin/', admin.site.urls),  # Enables admin
]

# Conditionally include urls for relevant active osdatascanner apps:
if (hasattr(settings, "OPTIONAL_APPS") and "debug_toolbar" in settings.OPTIONAL_APPS):
    import debug_toolbar
    urlpatterns.append(path('__debug__/', include(debug_toolbar.urls)))
