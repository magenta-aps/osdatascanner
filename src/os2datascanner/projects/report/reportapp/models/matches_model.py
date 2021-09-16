import structlog
from django.db import models
from django.utils.translation import ugettext_lazy as _
from os2datascanner.engine2.pipeline.messages import (
    MatchFragment,
    MetadataMessage,
    ProblemMessage,
)

from .documentreport_model import DocumentReport

logger = structlog.get_logger(__name__)


class Matches(models.Model):
    """Represent all matches from a single rule related to a specific resource

    This is basically a class to represent a `MatchFragment`
    """

    report = models.ForeignKey(DocumentReport, on_delete=models.CASCADE)
    rule = models.JSONField(null=False)
    matches = models.JSONField(null=False)

    # These fields can be reconstructed using MatchFragment from engine
    sensitivity = models.IntegerField(null=True, verbose_name=_("sensitivity"))
    probability = models.FloatField(null=True, verbose_name=_("probability"))
    rule_type = models.CharField(
        default="", max_length=256, verbose_name=_("rule type")
    )

    class Resolution(models.IntegerChoices):
        OTHER = 0, _("Other")
        EDITED = 1, _("Edited")
        MOVED = 2, _("Moved")
        REMOVED = 3, _("Removed")
        NO_ACTION = 4, _("No action")

    resolution_status = models.IntegerField(
        choices=Resolution.choices,
        null=True,
        blank=True,
        db_index=True,
        verbose_name=_("resolution status"),
    )

    resolution_time = models.DateTimeField(
        blank=True, null=True, verbose_name=_("resolution time")
    )

    # def __str__(self):
    #     return self.name

    def __repr__(self):
        return f"<{self.__class__.__name__}: ({self.rule}, {self.matches})>"

    class Meta:
        ordering = ["-sensitivity", "-probability", "rule_type", "pk"]
