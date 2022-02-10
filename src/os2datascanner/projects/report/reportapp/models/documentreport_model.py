import enum

from django.db import models
from django.core.exceptions import ValidationError
from django.db.models import JSONField
from django.utils.translation import ugettext_lazy as _
from .organization_model import Organization

from os2datascanner.utils.model_helpers import ModelFactory
from os2datascanner.utils.system_utilities import time_now
from os2datascanner.engine2.pipeline.messages import (
    MatchesMessage, ProblemMessage, MetadataMessage, ScanTagFragment
)
import structlog

logger = structlog.get_logger(__name__)


class DocumentReport(models.Model):
    factory = None

    scan_time = models.DateTimeField(null=True, db_index=True,
                                     verbose_name=_('scan time'))

    created_timestamp = models.DateTimeField(null=True,
                                             verbose_name=_('created timestamp'))

    organization = models.ForeignKey(Organization,
                                     null=True, blank=True,
                                     verbose_name=_('organization'),
                                     on_delete=models.PROTECT)

    path = models.CharField(max_length=2000, verbose_name=_("path"),
                            db_index=True)

    raw_scan_tag = JSONField(null=True)
    raw_matches = JSONField(null=True)
    raw_problem = JSONField(null=True)
    raw_metadata = JSONField(null=True)

    # sort results from a Source. It does not make sense to sort across Sources
    sort_key = models.CharField(
        max_length=256, verbose_name=_("sort key"), db_index=True, default=""
    )

    # the name of the specific resource a handle points to. The equivalent of a #
    # filename
    name = models.CharField(max_length=256, verbose_name=_("name"), default="")

    source_type = models.CharField(max_length=2000,
                                   verbose_name=_("source type"))

    sensitivity = models.IntegerField(null=True, verbose_name=_("sensitivity"))

    probability = models.FloatField(null=True, verbose_name=_("probability"))

    # datasource_last_modified stores when the scanned file/email/element itself,
    #  has last been updated.
    # This timestamp is collected during scan and is from the datasource.
    datasource_last_modified = models.DateTimeField(null=True)

    # Field to store the primary key of the scanner job that this DocumentReport stems from.
    scanner_job_pk = models.IntegerField(null=True)
    # Field to store name of the scanner job that this DocumentReport stems from.
    scanner_job_name = models.CharField(
        max_length=256,
        null=True,
        db_index=True,
    )

    def _str_(self):
        return self.path

    @property
    def scan_tag(self):
        return ScanTagFragment.from_json_object(self.raw_scan_tag)

    @property
    def matches(self):
        return (MatchesMessage.from_json_object(self.raw_matches)
                if self.raw_matches else None)

    @property
    def problem(self):
        return (ProblemMessage.from_json_object(self.raw_problem)
                if self.raw_problem else None)

    @property
    def metadata(self):
        return (MetadataMessage.from_json_object(self.raw_metadata)
                if self.raw_metadata else None)

    @property
    def presentation(self) -> str:
        """Get the handle presentation"""
        # get the Message. Only one of these will be non-None.
        type_msg = [msg for msg in
                    [self.matches, self.problem, self.metadata] if msg]
        # in case the report is still not updated with the Message, return empty
        # string
        if type_msg == []:
            return ""
        type_msg = type_msg[0]

        presentation = type_msg.handle.presentation if type_msg.handle else ""
        return presentation

    @property
    def scan_tag(self) -> ScanTagFragment:
        return (self.matches.scan_spec.scan_tag if self.matches
                else self.problem.scan_tag if self.problem
                else self.metadata.scan_tag if self.metadata else None)

    @enum.unique
    class ResolutionChoices(enum.Enum):
        # Future simplification note: the behaviour of the enumeration values
        # of this class is modelled on Django 3's model.Choices
        OTHER = 0, "Andet"
        EDITED = 1, "Redigeret"
        MOVED = 2, "Flyttet"
        REMOVED = 3, "Slettet"
        NO_ACTION = 4, "Intet foretaget"

        def __new__(cls, *args):
            obj = object.__new__(cls)
            # models.Choices compatibility: the last element of the enum value
            # tuple, if there is one, is a human-readable label
            obj._value_ = args[0] if len(args) < 3 else args[:-1]
            return obj

        def __init__(self, *args):
            self.label = args[-1] if len(args) > 1 else self.name

        # This is a class *property* in model.Choices, but that would require
        # sinister metaclass sorcery
        @classmethod
        def choices(cls):
            return [(k.value, k.label) for k in cls]

        def __repr__(self):
            return f"<{self.__class__.__name__}.{self.name}>"

    resolution_status = models.IntegerField(choices=ResolutionChoices.choices(),
                                            null=True, blank=True, db_index=True,
                                            verbose_name=_("resolution status"))

    resolution_time = models.DateTimeField(blank=True, null=True,
                                           verbose_name=_("resolution time"))

    custom_resolution_status = models.CharField(max_length=1024, blank=True,
                                                verbose_name=_("justification"))

    def clean(self):
        self.clean_custom_resolution_status()

    def clean_custom_resolution_status(self):
        self.custom_resolution_status = self.custom_resolution_status.strip()
        if self.resolution_status == 0 and not self.custom_resolution_status:
            raise ValidationError(
                    {
                        "custom_resolution_status":
                        "Resolution status 0 requires an"
                        " explanation"
                    })

    def __init__(self, *args, **kwargs):
        # TODO: move to property/model method
        super().__init__(*args, **kwargs)
        self.__resolution_status = self.resolution_status

    def save(self, *args, **kwargs):
        # If Resolution status goes from not handled to handled - change resolution_time to now
        if self.__resolution_status is None and (
                self.resolution_status or self.resolution_status == 0):
            self.resolution_time = time_now()

        # Adds a timestamp if it's a new match:
        if not self.pk:
            self.created_timestamp = time_now()

        # ensure model field constrains
        if len(old_name := self.name) > 256:
            self.name = self.name[:256]
        if len(old_sort_key := self.sort_key) > 256:
            self.sort_key = self.sort_key[:256]

        super().save(*args, **kwargs)

        # log after save, so self returns the Object pk.
        if len(old_name) > 256:
            logger.info("truncated name before saving", report=self, name=old_name)
        if len(old_sort_key) > 256:
            logger.info("truncated sort_key before saving", report=self,
                        sort_key=self.sort_key)

    class Meta:
        verbose_name_plural = _("document reports")
        ordering = ['-sensitivity', '-probability', 'pk']
        indexes = [
            models.Index("raw_matches__matched", name="documentreport_matched"),
        ]
        constraints = [
            models.UniqueConstraint(fields=["scanner_job_pk", "path"],
                                    name="unique_scanner_pk_and_path")
        ]


DocumentReport.factory = ModelFactory(DocumentReport)


@DocumentReport.factory.on_create
@DocumentReport.factory.on_update
def on_documentreport_created_or_updated(objects, fields=None):
    from .aliases.alias_model import Alias
    from .aliases.adsidalias_model import ADSIDAlias
    from .aliases.emailalias_model import EmailAlias
    from .aliases.webdomainalias_model import WebDomainAlias

    tm = Alias.match_relation.through
    new_objects = []
    for obj in objects:
        # Add DocumentReport to Alias.match_relation, when it's saved to the db.
        if not obj.metadata:
            continue
        if (email := obj.metadata.metadata.get("email-account")):
            email_alias = EmailAlias.objects.filter(address__iexact=email)
            add_new_relations(email_alias, new_objects, obj, tm)
        if (adsid := obj.metadata.metadata.get("filesystem-owner-sid")):
            adsid_alias = ADSIDAlias.objects.filter(sid=adsid)
            add_new_relations(adsid_alias, new_objects, obj, tm)
        if (web_domain := obj.metadata.metadata.get("web-domain")):
            web_domain_alias = WebDomainAlias.objects.filter(domain=web_domain)
            add_new_relations(web_domain_alias, new_objects, obj, tm)
    try:
        # TODO: We do not bulk create DocumentReports, and therefore will we always
        #  bulk_create 1 Alias.match_relation at the time. We do not actually
        #  use the bulk functionality.
        tm.objects.bulk_create(new_objects, ignore_conflicts=True)
    except Exception:
        logger.error("Failed to create match_relation", exc_info=True)


def add_new_relations(adsid_alias, new_objects, obj, tm):
    for alias in adsid_alias:
        new_objects.append(
            tm(documentreport_id=obj.pk, alias_id=alias.pk))

# TODO: #43340 (if we need to explicitly delete the instances of the implicit
# model class used by Alias.match_relation, we should also hook DocumentReport.
# factory.on_delete here)
