import enum
import datetime

from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.postgres.fields import JSONField
from .organization_model import Organization

from os2datascanner.engine2.pipeline.messages import MatchesMessage


class DocumentReport(models.Model):
    scan_time = models.DateTimeField(null=True)

    created_timestamp = models.DateTimeField(null=True, blank=True,
                                             verbose_name='Created timestamp')

    organization = models.ForeignKey(Organization,
                                     null=True, blank=True,
                                     verbose_name='Organisation',
                                     on_delete=models.PROTECT)

    path = models.CharField(max_length=2000, verbose_name="Path")
    # It could be that the meta data should not be part of the jsonfield...
    data = JSONField(null=True)

    sensitivity = models.IntegerField(null=True, verbose_name="Sensitivity")

    probability = models.FloatField(null=True, verbose_name="Probability")

    def _str_(self):
        return self.path

    @property
    def matches(self):
        matches = self.data.get("matches")
        return MatchesMessage.from_json_object(matches) if matches else None

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

    resolution_status = models.IntegerField(choices=ResolutionChoices.choices(),
                                            null=True, blank=True, db_index=True,
                                            verbose_name="Håndteringsstatus")

    resolution_time = models.DateTimeField(blank=True, null=True)

    custom_resolution_status = models.CharField(max_length=1024, blank=True,
                                                verbose_name="Begrundelse")

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
        super().__init__(*args, **kwargs)
        self.__resolution_status = self.resolution_status

    def save(self, *args, **kwargs):
        # If Resolution status goes from not handled to handled - change resolution_time to now 
        if self.__resolution_status == None and (self.resolution_status or self.resolution_status == 0):
            self.resolution_time = datetime.datetime.now()

        # Adds a timestamp if it's a new match:
        if not self.pk:
            self.created_timestamp = datetime.datetime.now()

        super().save(*args, **kwargs)


    class Meta:
        verbose_name_plural = "Document reports"
        ordering = ['-sensitivity', '-probability']

