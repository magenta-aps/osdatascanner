from django.db import models
from django.utils.translation import gettext_lazy as _, pgettext_lazy

from os2datascanner.engine2.model._staging import sbsysdb
from os2datascanner.projects.grants.models import SMBGrant
from .scanner import Scanner


class SBSYSDBScanner(Scanner):
    @classmethod
    def get_type(cls):
        return "sbsys-db"

    db_server = models.CharField(
            max_length=None,
            blank=False,
            verbose_name=_("SBSYS database server"),
            help_text=_(
                    "The network name of the SQL Server instance used by your"
                    " SBSYS installation."))
    db_port = models.IntegerField(
            verbose_name=_("SBSYS database service port"),
            default=1433,
            help_text=_(
                    "The port on which to connect to the SQL Server"
                    " instance."))
    db_name = models.CharField(
            max_length=None,
            blank=False,
            default="SbSysNetDrift",
            verbose_name=_("SBSYS database name"),
            help_text=_(
                    "The name of the SBSYS database."))

    weblink = models.CharField(
            max_length=None,
            blank=True,
            verbose_name=_("SBSYS A-sag link"),
            help_text=_(
                    "The base URL of the SBSYS A-sag instance for your SBSYS"
                    " installation, used to build web links to SBSYS cases."))

    grant = models.ForeignKey(
            SMBGrant, null=True,
            on_delete=models.SET_NULL,
            verbose_name=_("Service account"),
            help_text=_(
                    "A service account with access to the SQL Server"
                    " instance."))

    def generate_sources(self):
        if not self.grant:
            raise ValueError

        yield sbsysdb.SBSYSDBSource(
                self.db_server, self.db_port, self.db_name,
                self.grant.traditional_name, self.grant.password,
                reflect_tables=None,  # trust the defaults
                base_weblink=self.weblink or None)

    object_name = pgettext_lazy("unit of scan", "case")
    object_name_plural = pgettext_lazy("unit of scan", "cases")

    class Meta:
        verbose_name = _("SBSYS database scanner")
        verbose_name_plural = _("SBSYS database scanners")
