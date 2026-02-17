# Part of the OSdatascanner system, copyright © 2014-2026 Magenta ApS.
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, you can
# obtain one at http://mozilla.org/MPL/2.0/.

import structlog
from django.db import models
from django.utils.translation import gettext_lazy as _

from model_utils.managers import InheritanceManager

logger = structlog.get_logger("import_services")


class ImportService(models.Model):
    """Non-abstract parent class for any import service class.

    An ImportService represents the (optional) external identity management
    system for an Organization. When configured, an ImportService allows the
    OSdatascanner system to import relevant Accounts, OrganizationalUnits and
    Positions from the external system.

    NB! Should not be instantiated on its own! It is kept non-abstract to
    ensure one unifying table in the database, to support the one-to-one
    restriction, which in turn ensures a single source of truth for imports.
    """

    objects = InheritanceManager()

    organization = models.OneToOneField(
        'organizations.Organization',
        primary_key=True,
        on_delete=models.CASCADE,
        verbose_name=_('organization UUID'),
    )

    hide_units_on_import = models.BooleanField(
        default=False,
        verbose_name=_('hide new units on import'),
        help_text=_("hide new organizational units by default"),
    )

    def start_import(self):
        """Method for providing source-config specific details to _start_import_job,
         which will create a new import job if possible. """
        logger.warning("start_import() not implemented on model!"
                       "Perhaps you're looking for a subclass?", model=type(self).__name__
                       )

    class Meta:
        verbose_name = _('import service')
        verbose_name_plural = _('import services')

    def __str__(self):
        cls = self.__class__.__name__
        format_string = _("{cls} for {org}")
        return format_string.format(org=self.organization, cls=cls)

    def __repr__(self):
        cls = self.__class__.__name__
        return f"<{cls} for {self.organization_id} (Organization)>"
