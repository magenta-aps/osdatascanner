from django.apps import AppConfig


class OSdatascannerSharedConfig(AppConfig):
    # the name needs to be changed as soon as the directive is renamed to "osdatascanner"
    name = "os2datascanner.projects.shared"
    label = 'osdatascanner_shared'
    verbose_name = "OSdatascanner shared UI resources"
    default = True
