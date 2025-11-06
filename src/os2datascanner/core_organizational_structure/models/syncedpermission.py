from django.db import models
from django.utils.translation import gettext_lazy as _


class SyncedPermission(models.Model):
    """This model is not intended to ever store anything in the database.
       it only exists as a model to define permissions for. These permissions will exist both
       in the admin and report module."""

    class Meta:
        abstract = True
        permissions = [
            # SBSYS
            ("view_sbsys_tab", _("Can view the SBSYS tab in the report module")),
            # Leader Statistics Page
            ("filter_scannerjob_leader_overview",
                _("Can filter by scannerjob in the leader overview")),
            # Scannerjob list
            ("view_scannerjob_list", _("Can view the scannerjob list in the report module")),
            ("delete_documentreports", _("Can permanently delete reports in the report module")),
            # Withheld results
            ("view_withheld_results",
                _("Can view the withheld results tab in the report module")),
            ("handle_withheld_results",
                _("Can handle withheld results in the report module")),
            ("distribute_withheld_results",
                _("Can distribute withheld results to users in the report module"))
        ]
