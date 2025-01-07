from django.conf import settings
from django.utils.translation import pgettext_lazy
from django.urls import reverse_lazy
from .scanner import Scanner

from os2datascanner.engine2.model.sbsys import SbsysSource


class SbsysScanner(Scanner):
    def get_type(self):
        return 'sbsys'

    def get_absolute_url(self):
        return '/sbsysscanners'

    @staticmethod
    def get_create_url():
        return reverse_lazy("sbsysscanner_add")

    def get_update_url(self):
        return reverse_lazy("sbsysscanner_update", kwargs={"pk": self.pk})

    def get_cleanup_url(self):
        return reverse_lazy("sbsysscanner_cleanup", kwargs={"pk": self.pk})

    def get_askrun_url(self):
        return reverse_lazy("sbsysscanner_askrun", kwargs={"pk": self.pk})

    def get_copy_url(self):
        return reverse_lazy("sbsysscanner_copy", kwargs={"pk": self.pk})

    def get_remove_url(self):
        return reverse_lazy("sbsysscanner_remove", kwargs={"pk": self.pk})

    def get_delete_url(self):
        return reverse_lazy("sbsysscanner_delete", kwargs={"pk": self.pk})

    def generate_sources(self):
        yield SbsysSource(
            client_id=settings.SBSYS_CLIENT_ID,
            client_secret=settings.SBSYS_CLIENT_SECRET,
            token_url=settings.SBSYS_TOKEN_URL,
            api_url=settings.SBSYS_API_URL
        )

    object_name = pgettext_lazy("unit of scan", "case")
    object_name_plural = pgettext_lazy("unit of scan", "cases")
