from django.db import models
from django.utils.translation import gettext_lazy as _, pgettext_lazy
from django.conf import settings
import structlog

from os2datascanner.utils.ref import Counter
from os2datascanner.engine2.model._staging import sbsysdb, sbsysdb_rule
from os2datascanner.engine2.rules.logical import AndRule
from os2datascanner.engine2.pipeline import messages
from os2datascanner.projects.grants.models import SMBGrant

from ....organizations.models.aliases import AliasType
from .scanner import Scanner


logger = structlog.get_logger("adminapp")


class SBSYSDBScanner(Scanner):
    _supports_account_annotations = True  # sort of :D

    @classmethod
    def get_type(cls):
        return "sbsys-db"

    @staticmethod
    def enabled():
        return settings.ENABLE_SBSYSSCAN

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

    def _yield_sources(
            self, spec_template: messages.ScanSpecMessage, force: bool,
            source_counter: Counter | None = None):
        # Normally this method yields one ScanSpecMessage for each
        # CoveredAccount, but that's not how SBSYS scans work. Instead, we
        # yield a single scan spec with a tweaked Rule that filters out
        # everything not associated with a CoveredAccount
        covered_accs = self.compute_covered_accounts()
        source, = self.generate_sources()

        upn_set = set()
        for acc in covered_accs:
            acc_upns = {a._value
                        for a in acc.aliases.filter(
                                _alias_type=AliasType.USER_PRINCIPAL_NAME)}
            logger.debug(
                    "computed UPN set for account",
                    scanner=self, account=acc, upn_set=acc_upns)
            upn_set |= acc_upns
        if not upn_set:
            # No UPNs to scan, so don't emit a Source at all. Failing early is
            # better than submitting a broken scan
            logger.error(
                    "final UPN set is empty, not creating a Source",
                    scanner=self)
            return

        Counter.try_incr(source_counter)
        yield spec_template._replace(
                source=source,
                rule=AndRule.make(
                        sbsysdb_rule.SBSYSDBRule(
                                "Behandler.UserPrincipalName",
                                "iin",
                                list(upn_set),
                                synthetic=True),
                        spec_template.rule))

    class Meta:
        verbose_name = _("SBSYS database scanner")
        verbose_name_plural = _("SBSYS database scanners")
