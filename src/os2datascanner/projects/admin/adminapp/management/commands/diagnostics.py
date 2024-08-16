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
from django.db.models import Count, Q
from django.conf import settings

from ....organizations.models import Account, Alias, OrganizationalUnit, Organization
from ...models.usererrorlog import UserErrorLog
from ...models.rules import CustomRule


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
        self.stdout.write("\n\n>> Running diagnostics on accounts ...")
        accounts = Account.objects.all()
        accounts_without_username = accounts.filter(username="").values("pk")
        accounts_without_email = accounts.filter(email="").values("pk")
        imported_accounts = accounts.filter(imported=True)
        imported_accounts_no_positions = imported_accounts.filter(
            positions__isnull=True).values("pk")

        self.stdout.write(
            f"Found a total of {accounts.count()} accounts. "
            f"{imported_accounts.count()} are imported.")

        if accounts_without_username:
            self.stdout.write(f"Found {len(accounts_without_username)} "
                              "accounts without a username: " +
                              ", ".join([str(d["pk"]) for d in accounts_without_username]))

        if accounts_without_email:
            self.stdout.write(f"Found {len(accounts_without_email)} accounts without an email: " +
                              ", ".join([str(d["pk"]) for d in accounts_without_email]))

        if imported_accounts_no_positions:
            self.stdout.write(f"Found {len(imported_accounts_no_positions)} imported "
                              "accounts without relation to an OrganizationalUnit: " +
                              ", ".join([str(d["pk"]) for d in imported_accounts_no_positions]))

    def diagnose_aliases(self):
        self.stdout.write("\n\n>> Running diagnostics on aliases ...")
        aliases = Alias.objects.all()
        alias_types = aliases.values(
            "_alias_type").order_by().annotate(count=Count("_alias_type"))
        aliases_with_no_account = aliases.filter(account__isnull=True).values("pk")

        nl = '\n  '
        self.stdout.write(
            f"Found a total of {aliases.count()} aliases: \n  "
            f"{nl.join([f'''{a['_alias_type']}: {a['count']}''' for a in alias_types])}")

        # This cannot actually happen due to db constraints. Remove?
        if aliases_with_no_account:
            self.stdout.write(f"Found {len(aliases_with_no_account)} aliases with no account:",
                              ", ".join([str(d['pk']) for d in aliases_with_no_account]))

    def diagnose_errors(self):
        self.stdout.write("\n\n>> Running diagnostics on errors ...")
        all_errors = UserErrorLog.objects.all()
        errors = all_errors.values("error_message").order_by().annotate(
            count=Count("error_message")).order_by("-count")

        if errors.exists():
            self.stdout.write(
                f"Found {errors.count()} different errors ({all_errors.count()} "
                "errors in total). Now presenting the 5 most common:")

            for message_dict in errors[:5]:
                self.stdout.write(
                    f"  ({message_dict['count']} counts) {message_dict['error_message']}")

    def diagnose_units(self):
        self.stdout.write("\n\n>> Running diagnostics on units ...")
        units = OrganizationalUnit.objects.count()

        self.stdout.write(f"Found {units} units.")

    def diagnose_organizations(self):
        self.stdout.write("\n\n>> Running diagnostics on organizations ...")
        orgs = Organization.objects.all()

        self.stdout.write(f"Found {len(orgs)} organizations.")

        for os in orgs.filter(Q(name="OS2datascanner") | Q(name="OSdatascanner")):
            self.stdout.write(
                f"The organization with UUID {os.pk} is called '{os.name}'."
                " Should this be changed?'")

        self.stdout.write("\nOverview of organizations:")
        for org in orgs:
            self.stdout.write(org.name)
            self.stdout.write(
                f"  Notification schedule: {org.email_notification_schedule}")
            self.stdout.write("  Contact information:")
            self.stdout.write(f"  * Email: {org.contact_email}")
            self.stdout.write(f"  * Phone: {org.contact_phone}")
            self.stdout.write("Settings:")
            self.stdout.write(
                f"  * Outlook delete email permission: {org.outlook_delete_email_permission}")
            self.stdout.write(
                f"  * Outlook categorize email permission: "
                f"{org.get_outlook_categorize_email_permission_display()}")
            self.stdout.write(
                f"  * OneDrive/SharePoint delete permission: {org.onedrive_delete_permission}")
            self.stdout.write(f"  * Leadertab access: {org.get_leadertab_access_display()}")
            self.stdout.write(
                f"  * DPO-tab access: {org.get_dpotab_access_display()}")
            self.stdout.write(f"  * Show Support Button: {org.show_support_button}")
            self.stdout.write(
                f"  * Support Contact Method: {org.get_support_contact_method_display()}")
            self.stdout.write(f"  * Support Name: {org.support_name}")
            self.stdout.write(f"  * Support Value: {org.support_value}")
            self.stdout.write(f"  * DPO Contact Method: {org.get_dpo_contact_method_display()}")
            self.stdout.write(f"  * DPO Name: {org.dpo_name}")
            self.stdout.write(f"  * DPO Value: {org.dpo_value}")

    def diagnose_rules(self):
        self.stdout.write("\n\n>> Running diagnostics on rules ...")
        rules = CustomRule.objects.all()

        self.stdout.write(f"Found {rules.count()} custom rules:")
        for rule in rules:
            self.stdout.write(f"\n===={rule.name}====")
            self.stdout.write(f"Description:\n\"{rule.description}\"")

            has_scanners = False
            if scanners := rule.scanners.all():
                has_scanners = True
                self.stdout.write("\nScanners (regular rules):")
                [self.stdout.write(f"· {scanner.name} ({scanner.pk})") for scanner in scanners]
            if ex_scanners := rule.scanners_ex_rule.all():
                has_scanners = True
                self.stdout.write("\nScanners (exclusion rules):")
                [self.stdout.write(f"· {scanner.name} ({scanner.pk})") for scanner in ex_scanners]
            if not has_scanners:
                self.stdout.write("\nNo connected scanners.")

            # We run this through a JSON-formatter to print it prettier.
            self.stdout.write("\nRule JSON:")
            self.stdout.write(json.dumps(rule._rule, indent=2))

    def diagnose_settings(self):
        self.stdout.write("\n\n>> Running diagnostics on settings ...")
        if settings.DEBUG:
            self.stdout.write("\nWARNING: DEBUG is ON for this installation!")

        def print_settings(*attributes):
            for attribute in attributes:
                self.stdout.write(f"{attribute} = {getattr(settings, attribute)!r}")

        self.stdout.write("\n//INSTALLATION-WIDE SETTINGS//")

        self.stdout.write("\n# [functionality]")
        print_settings("EXCLUSION_RULES", "ANALYSIS_PAGE",
                       "AUTOMATIC_IMPORT_CLEANUP", "MANUAL_PAGE",
                       "USERERRORLOG")

        self.stdout.write("\n# [scans]")
        print_settings("ENABLE_FILESCAN", "ENABLE_WEBSCAN",
                       "ENABLE_EXCHANGESCAN", "ENABLE_DROPBOXSCAN",
                       "ENABLE_MSGRAPH_MAILSCAN", "ENABLE_MSGRAPH_FILESCAN",
                       "ENABLE_MSGRAPH_CALENDARSCAN",
                       "ENABLE_MSGRAPH_TEAMS_FILESCAN",
                       "ENABLE_GOOGLEDRIVESCAN", "ENABLE_GMAILSCAN",
                       "ENABLE_SBSYSSCAN")

        self.stdout.write("\n# [logging]")
        print_settings("LOG_LEVEL")

        self.stdout.write("\n# [other]")
        print_settings("ENABLE_MINISCAN", "MINISCAN_REQUIRES_LOGIN",
                       "MINISCAN_FILE_SIZE_LIMIT")

        self.stdout.write("\n//ENVIRONMENT VARIABLES//")

        for key, val in dict(environ).items():
            self.stdout.write(f"{key} = {val!r}")

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
