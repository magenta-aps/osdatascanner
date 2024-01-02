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
import json
from os import environ

from django.core.management.base import BaseCommand
from django.db.models import Count
from django.conf import settings

from ....organizations.models import Account, Alias, OrganizationalUnit, Organization
from ...models.usererrorlog import UserErrorLog
from ...models.rules.customrule import CustomRule


class Command(BaseCommand):
    """Run diagnostics on the admin module."""

    help = __doc__

    choice_list = ["Account", "Alias", "UserErrorLog", "OrganizationalUnit",
                   "Organization", "Rule", "Settings"]

    def add_arguments(self, parser):
        parser.add_argument(
            "--only",
            default=False,
            choices=self.choice_list,
            nargs="+",
            help="Only run diagnostics on a specific part of the admin module.")

    def diagnose_accounts(self):
        print("\n\n>> Running diagnostics on accounts ...")
        accounts = Account.objects.all()
        accounts_without_username = accounts.filter(username="").values("pk")

        print(f"Found a total of {accounts.count()} accounts.")

        if accounts_without_username:
            print(f"Found {len(accounts_without_username)} accounts without a username:", ", ".join(
                [d["pk"] for d in accounts_without_username]))

    def diagnose_aliases(self):
        print("\n\n>> Running diagnostics on aliases ...")
        aliases = Alias.objects.all()
        alias_types = aliases.values(
            "_alias_type").order_by().annotate(count=Count("_alias_type"))
        aliases_with_no_account = aliases.filter(account__isnull=True).values("pk")

        nl = '\n  '
        print(
            f"Found a total of {aliases.count()} aliases: \n  "
            f"{nl.join([f'''{a['_alias_type']}: {a['count']}''' for a in alias_types])}")

        if aliases_with_no_account:
            print(f"Found {len(aliases_with_no_account)} aliases with no account:",
                  ", ".join([str(d['pk']) for d in aliases_with_no_account]))

    def diagnose_errors(self):
        print("\n\n>> Running diagnostics on errors ...")
        all_errors = UserErrorLog.objects.all()
        errors = all_errors.values("error_message").order_by().annotate(
            count=Count("error_message")).order_by("-count")

        if errors.exists():
            print(
                f"Found {errors.count()} different errors ({all_errors.count()} "
                "errors in total). Now presenting the 5 most common:")

            for message_dict in errors[:5]:
                print(
                    f"  ({message_dict['count']} counts) {message_dict['error_message']}")

    def diagnose_units(self):
        print("\n\n>> Running diagnostics on units ...")
        units = OrganizationalUnit.objects.count()

        print(f"Found {units} units.")

    def diagnose_organizations(self):
        print("\n\n>> Running diagnostics on organizations ...")
        orgs = Organization.objects.all()

        print(f"Found {len(orgs)} organizations.")

        if os2 := orgs.filter(name="OS2datascanner").first():
            print(
                f"The organization with UUID {os2.pk} is called 'OS2datascanner'."
                " Should this be changed?'")

        print("\nOverview of organizations:")
        for org in orgs:
            print(org.name)
            print(
                f"  Notification schedule: {org.email_notification_schedule}")
            print("  Contact information:")
            print("  * Email:", org.contact_email)
            print("  * Phone:", org.contact_phone)
            print("  Settings:")
            print("  * MSGraph Write Permissions:", org.get_msgraph_write_permissions_display())
            print("  * Leadertab access:", org.get_leadertab_access_display())
            print(
                "  * DPO-tab access:",
                org.get_dpotab_access_display())
            print("  * Show Support Button:", org.show_support_button)
            print("  * Support Contact Method:", org.get_support_contact_method_display())
            print("  * Support Name:", org.support_name)
            print("  * Support Value:", org.support_value)
            print("  * DPO Contact Method:", org.get_dpo_contact_method_display())
            print("  * DPO Name:", org.dpo_name)
            print("  * DPO Value:", org.dpo_value)

    def diagnose_rules(self):
        print("\n\n>> Running diagnostics on rules ...")
        rules = CustomRule.objects.all()

        print(f"Found {rules.count()} custom rules:")
        for rule in rules:
            print(f"\n===={rule.name}====")
            print(f"Description:\n\"{rule.description}\"")

            has_scanners = False
            if scanners := rule.scanners.all():
                has_scanners = True
                print("\nScanners (regular rules):")
                [print(f"· {scanner.name} ({scanner.pk})") for scanner in scanners]
            if ex_scanners := rule.scanners_ex_rules.all():
                has_scanners = True
                print("\nScanner (exclusion rules):")
                [print(f"· {scanner.name} ({scanner.pk})") for scanner in ex_scanners]
            if not has_scanners:
                print("\nNo connected scanners.")

            # We run this through a JSON-formatter to print it prettier.
            print("\nRule JSON:")
            print(json.dumps(rule._rule, indent=2))

    def diagnose_settings(self):
        print("\n\n>> Running diagnostics on settings ...")
        if settings.DEBUG:
            print("\nWARNING: DEBUG is ON for this installation!")

        def print_settings(*attributes):
            for attribute in attributes:
                print(f"{attribute} = {getattr(settings, attribute)!r}")

        print("\n//INSTALLATION-WIDE SETTINGS//")

        print("\n# [functionality]")
        print_settings("EXCLUSION_RULES", "ANALYSIS_PAGE",
                       "AUTOMATIC_IMPORT_CLEANUP", "MANUAL_PAGE",
                       "USERERRORLOG")

        print("\n# [scans]")
        print_settings("ENABLE_FILESCAN", "ENABLE_WEBSCAN",
                       "ENABLE_EXCHANGESCAN", "ENABLE_DROPBOXSCAN",
                       "ENABLE_MSGRAPH_MAILSCAN", "ENABLE_MSGRAPH_FILESCAN",
                       "ENABLE_MSGRAPH_CALENDARSCAN",
                       "ENABLE_MSGRAPH_TEAMS_FILESCAN",
                       "ENABLE_GOOGLEDRIVESCAN", "ENABLE_GMAILSCAN",
                       "ENABLE_SBSYSSCAN")

        print("\n# [logging]")
        print_settings("DJANGO_LOG_LEVEL")

        print("\n# [other]")
        print_settings("ENABLE_MINISCAN", "MINISCAN_REQUIRES_LOGIN",
                       "MINISCAN_FILE_SIZE_LIMIT", "DATA_UPLOAD_MAX_NUMBER_FIELDS")

        print("\n//ENVIRONMENT VARIABLES//")

        for key, val in dict(environ).items():
            print(f"{key} = {val!r}")

    def handle(self, only, **options):

        if not only:
            only = self.choice_list

        for opt in only:
            match opt:
                case "Account":
                    self.diagnose_accounts()
                case "Alias":
                    self.diagnose_aliases()
                case "UserErrorLog":
                    self.diagnose_errors()
                case "OrganizationalUnit":
                    self.diagnose_units()
                case "Organization":
                    self.diagnose_organizations()
                case "Rule":
                    self.diagnose_rules()
                case "Settings":
                    self.diagnose_settings()
