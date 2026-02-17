# Part of the OSdatascanner system, copyright © 2014-2026 Magenta ApS.
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, you can
# obtain one at http://mozilla.org/MPL/2.0/.

from ..organizations.models import Organization
from .models import Client
from ..import_services.models.import_service import ImportService


def clear_import_services(client: Client):
    organizations = Organization.objects.filter(client=client)

    for org in organizations:
        import_services = ImportService.objects.filter(organization=org)
        import_services.delete()
