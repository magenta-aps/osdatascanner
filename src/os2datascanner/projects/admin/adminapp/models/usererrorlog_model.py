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

    # hidden = models.BooleanField(
    #     default=False
    # )

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
