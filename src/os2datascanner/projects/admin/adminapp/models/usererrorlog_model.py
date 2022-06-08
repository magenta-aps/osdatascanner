import enum

from django.db import models
from django.utils.translation import ugettext_lazy as _

from .scannerjobs.scanner_model import ScanStatus


translation_table = {
    "Exploration error. MemoryError: 12, Cannot allocate memory":
    _("Folder at the path is using outdated encoding. Please "
      "rename the folder."),
}


class UserErrorLog(models.Model):

    """Model for logging errors relevant for the user."""

    scan_status = models.ForeignKey(
        ScanStatus,
        on_delete=models.CASCADE
    )
    path = models.CharField(
        max_length=1024,
        verbose_name=_('Path'),
        blank=True
    )
    error_message = models.CharField(
        max_length=1024,
        verbose_name=_('Error message')
    )

    @enum.unique
    class ArchiveChoices(enum.Enum):
        ARCHIVED = 0, "Arkiveret"
        NO_ACTION = 1, "Intet foretaget"

        def __new__(cls, *args):
            obj = object.__new__(cls)
            # models.Choices compatibility: the last element of the enum value
            # tuple, if there is one, is a human-readable label
            obj._value_ = args[0] if len(args) < 3 else args[:-1]
            return obj

        def __init__(self, *args):
            self.label = args[-1] if len(args) > 1 else self.name

        @classmethod
        def choices(cls):
            return [(k.value, k.label) for k in cls]

        def __repr__(self):
            return f"<{self.__class__.__name__}.{self.name}>"

    archive_status = models.IntegerField(
        choices=ArchiveChoices.choices(),
        null=True, blank=True, db_index=True,
        verbose_name=_("archive status")
    )

    @property
    def user_friendly_error_message(self):
        """Translates an error message into a meaningful instruction
        for the user, if one is available."""
        if self.error_message in translation_table.keys():
            return translation_table[self.error_message]
        else:
            return self.error_message

    # def hide(self):
    #     self.hidden = True
