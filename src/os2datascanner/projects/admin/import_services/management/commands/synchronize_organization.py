#!/usr/bin/env python
# The contents of this file are subject to the Mozilla Public License
# Version 2.0 (the "License"); you may not use this file except in
# compliance with the License. You may obtain a copy of the License at
#    http://www.mozilla.org/MPL/
#
# Software distributed under the License is distributed on an "AS IS"basis,
# WITHOUT WARRANTY OF ANY KIND, either express or implied. See the License
# for the specific language governing rights and limitations under the
# License.
#
# OS2datascanner was developed by Magenta in collaboration with OS2 the
# Danish community of open source municipalities (https://os2.eu/).
#
# The code is currently governed by OS2 the Danish community of open
# source municipalities ( https://os2.eu/ )
import structlog
from django.core.management import BaseCommand

from os2datascanner.projects.admin.import_services.models import ImportService
from os2datascanner.projects.admin.import_services.models import LDAPConfig
from os2datascanner.projects.admin.import_services.models import MSGraphConfiguration
from os2datascanner.projects.admin.import_services.models import OS2moConfiguration
from os2datascanner.projects.admin.import_services.utils import start_ldap_import, \
    start_msgraph_import, start_os2mo_import
from os2datascanner.utils.system_utilities import time_now

"""
    This command should be run by a cron job at the desired time
    organizational synchronizations should take place.
"""

logger = structlog.get_logger("import_services")


class Command(BaseCommand):

    help = "Run organization synchronization for current configured type(s):"

    def add_arguments(self, parser):
        parser.add_argument(
            "-f", "--force",
            action="store_true",
            help="Run organization synchronization regardless of schedulation.",
        )

    def handle(self, *args, force: bool = False, **kwargs):
        for conf in ImportService.objects.select_subclasses().all():

            scheduled_now = self.schedule_check(conf.organization) if not force else force

            if scheduled_now:
                if isinstance(conf, LDAPConfig):
                    start_ldap_import(conf)
                elif isinstance(conf, MSGraphConfiguration):
                    start_msgraph_import(conf)
                elif isinstance(conf, OS2moConfiguration):
                    start_os2mo_import(conf)
                else:
                    logger.warning(f"ignoring unknown import service {type(conf).__name__}")

            else:
                logger.info(
                    f"Skipping import service {type(conf).__name__} as it is not scheduled now.")

    def schedule_check(self, org):

        if not org.synchronization_hour:
            # Org doesn't have mail notifications scheduled/have disabled it.
            self.stdout.write(f"Organization {org.name} has no set synchronization hour.",
                              style_func=self.style.WARNING)
            return False

        else:
            current_hour = time_now().hour
            return current_hour == org.synchronization_hour
