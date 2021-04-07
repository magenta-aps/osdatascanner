from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class DirectoryServicesConfig(AppConfig):
    name = 'os2datascanner.projects.admin.directory_services'
    label = 'directory_services'
    verbose_name = _('directory services')
