from django.conf import settings
from django.utils.translation import pgettext_lazy
from .scanner import Scanner

from os2datascanner.engine2.model.sbsys import SbsysSource


class SbsysScanner(Scanner):

    @staticmethod
    def get_type():
        return 'sbsys'

    def generate_sources(self):
        yield SbsysSource(
            client_id=settings.SBSYS_CLIENT_ID,
            client_secret=settings.SBSYS_CLIENT_SECRET,
            token_url=settings.SBSYS_TOKEN_URL,
            api_url=settings.SBSYS_API_URL
        )

    object_name = pgettext_lazy("unit of scan", "case")
    object_name_plural = pgettext_lazy("unit of scan", "cases")
