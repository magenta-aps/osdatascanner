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
import termplotlib as tpl
from os import environ


from django.core.management.base import BaseCommand
from django.db.models import Count, F, Q
from django.db.models.functions import Lower
from django.conf import settings

from ....organizations.models import Account, Alias, OrganizationalUnit, Organization
from ...models.documentreport import DocumentReport


class Command(BaseCommand):
    """Run diagnostics on the report module."""

    help = __doc__

    choice_list = ["Account", "Alias", "DocumentReport", "OrganizationalUnit",
                   "Organization", "Problem", "Settings"]

    def add_arguments(self, parser):
        parser.add_argument(
            "--only",
            default=False,
            choices=self.choice_list,
            nargs="+",
            help="Only run diagnostics on a specific part of the report module.")

    def diagnose_accounts(self):
        self.stdout.write("\n\n>> Running diagnostics on accounts ...")
        accounts = Account.objects.all()
        accounts_without_username = accounts.filter(username="").values("pk")
        accounts_without_email = accounts.filter(email="").values("pk")
        accounts_without_user = accounts.filter(user__isnull=True).values("username", "pk")
        username_counts = accounts.annotate(username_lower=Lower("username")
                                            ).values("username_lower").order_by(
        ).annotate(count=Count("username_lower")).order_by("-count").filter(count__gte=2)

        self.stdout.write(f"Found a total of {accounts.count()} accounts.")

        if accounts_without_username:
            self.stdout.write(f"Found {len(accounts_without_username)} "
                              "accounts without a username: " + ", ".join(
                                  [str(d["pk"]) for d in accounts_without_username]))

        if accounts_without_email:
            self.stdout.write(f"Found {len(accounts_without_email)} "
                              "accounts without an email:" + ", ".join(
                                  [str(d["pk"]) for d in accounts_without_email]))

        if accounts_without_user:
            self.stdout.write(f"Found {len(accounts_without_user)} "
                              "accounts without a user: " + ", ".join(
                                  [f'''{d['username']} ({str(d['pk'])})'''
                                   for d in accounts_without_user]))

        if username_counts:
            self.stdout.write(f"Found {len(username_counts)} cases of duplicate usernames "
                              "(disregarding case): " + ", ".join(
                                  [f"{d['username_lower']} ({d['count']})"
                                   for d in username_counts]))

        if settings.MSGRAPH_ALLOW_WRITE:
            accounts_missing_categories = accounts.annotate(
                categories=Count("outlook_settings__outlook_categories")).filter(
                categories__lt=2).values("pk")
            if accounts_missing_categories:
                self.stdout.write(f"Found {len(accounts_missing_categories)} accounts missing "
                                  "one or more Outlook categories: " + (" ".join(
                                      [str(d["pk"]) for d in accounts_missing_categories])))

    def diagnose_aliases(self):
        self.stdout.write("\n\n>> Running diagnostics on aliases ...")
        aliases = Alias.objects.all()
        alias_types = aliases.values(
            "_alias_type").order_by().annotate(count=Count("_alias_type"))
        # We have to make new querysets here, as annotating with Count
        # Will always give "0" if the counted field is null.
        aliases_with_no_account = aliases.filter(account__isnull=True).values("pk")
        aliases_with_mismatched_account_user = aliases.exclude(
            user=F("account__user")).values('pk')

        nl = '\n  '
        self.stdout.write(
            f"Found a total of {aliases.count()} aliases: \n  "
            f"{nl.join([f'''{a['_alias_type']}: {a['count']}''' for a in alias_types])}")

        if aliases_with_no_account:
            self.stdout.write(f"Found {len(aliases_with_no_account)} aliases with no account: " +
                              ", ".join([str(d['pk']) for d in aliases_with_no_account]))

        if aliases_with_mismatched_account_user:
            self.stdout.write(f"Found {len(aliases_with_mismatched_account_user)} aliases "
                              "with mismatched accounts and users: " +
                              ", ".join(
                                [str(d['pk']) for d in aliases_with_mismatched_account_user]))

    def diagnose_problems(self):
        self.stdout.write("\n\n>> Running diagnostics on problems ...")
        all_problems = DocumentReport.objects.filter(raw_problem__isnull=False)
        problems = all_problems.values("raw_problem__message").order_by().annotate(
            count=Count("raw_problem__message")).order_by("-count")

        if problems:
            self.stdout.write(
                f"Found {len(problems)} different problems ({all_problems.count()} "
                "problems in total). Now presenting the 5 most common:")

            for message_dict in problems[:5]:
                self.stdout.write(
                    f"  ({message_dict['count']} counts) {message_dict['raw_problem__message']}")

    def diagnose_reports(self):
        self.stdout.write("\n\n>> Running diagnostics on reports ...")
        reports = DocumentReport.objects.all()
        matches = reports.filter(number_of_matches__gte=1)
        handled = matches.filter(
            resolution_status__isnull=False).values("resolution_status").order_by().annotate(
            count=Count("resolution_status")).order_by("-count")
        unhandled = matches.filter(resolution_status__isnull=True)
        scannerjobs = matches.values(
            "scanner_job_pk", "scanner_job_name").order_by().annotate(
            count=Count("pk")).order_by("-count")

        self.stdout.write(f"Found {reports.count()} reports in total, {matches.count()} of which "
                          f"contain matches, {unhandled.count()} of which are unhandled.")

        if handled:
            self.stdout.write("\nMatches are handled in the following way:")
            labels = [
                DocumentReport.ResolutionChoices(
                    res_dict['resolution_status']).label for res_dict in handled]
            counts = [res_dict['count'] for res_dict in handled]
            # Create figure in the terminal
            fig = tpl.figure()
            fig.barh(counts, labels)
            fig.show()

        if matches:
            self.stdout.write("\nMatches come from the following scannerjobs:")
            labels = [
                f"{scannerjob['scanner_job_name']} ({scannerjob['scanner_job_pk']})"
                for scannerjob in scannerjobs]
            counts = [scannerjob['count'] for scannerjob in scannerjobs]

            # Create figure in the terminal
            fig = tpl.figure()
            fig.barh(counts, labels)
            fig.show()

        # Check for timestamps
        no_created_timestamp = reports.filter(created_timestamp__isnull=True)
        no_resolution_time = reports.filter(
            resolution_status__isnull=False, resolution_time__isnull=True)
        no_both_timestamps = no_created_timestamp & no_resolution_time

        if no_created_timestamp.count():
            self.stdout.write(
                f"Found {no_created_timestamp.count()} reports without a 'created_timestamp'.")
        if no_resolution_time.count():
            self.stdout.write(f"Found {no_resolution_time.count()} handled reports without"
                              f" a 'resolution_time'.")
        if no_both_timestamps.count():
            self.stdout.write(
                f"Found {no_both_timestamps.count()} handled reports without "
                f"both a 'created_timestamp' and a 'resolution_time'.")

        # Check for reports handled before they were created
        impossible_timestamps = reports.filter(
            resolution_status__isnull=False,
            created_timestamp__gt=F("resolution_time"))

        if impossible_timestamps.count():
            self.stdout.write(
                f"Found {impossible_timestamps.count()} handled reports, where"
                f" the 'resolution_time' is earlier than the 'created_timestamp'.")

        # Check for unrelated reports
        unrelated_matches = matches.filter(alias_relation__isnull=True)

        if unrelated_matches.count():
            self.stdout.write(f"Found {unrelated_matches.count()} matched reports "
                              "without a relation to an alias.")

        # Top five matched accounts
        account_matches = matches.values("alias_relation__account__username").order_by(
            ).annotate(count=Count("alias_relation__account__username")).order_by("-count")

        if account_matches:
            self.stdout.write("\nPresenting the five accounts with most matched reports:")
            nl = '\n  '
            self.stdout.write(" " + nl.join(
                [f"{acc['alias_relation__account__username']}: {acc['count']} "
                 "matched reports" for acc in account_matches[:5] if acc['count']]))

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

            self.stdout.write("  Settings:")
            self.stdout.write(
                f"  * Outlook delete email permission: {org.outlook_delete_email_permission}")
            self.stdout.write(
                f"  * Outlook categorize email permission: "
                f"{org.get_outlook_categorize_email_permission_display()}")
            self.stdout.write(f"  * Onedrive delete permission: {org.onedrive_delete_permission}")
            self.stdout.write(f"  * Leadertab access: {org.get_leadertab_access_display()}")
            self.stdout.write(f"  * DPO-tab access: {org.get_dpotab_access_display()}")
            self.stdout.write(f"  * Show Support Button: {org.show_support_button}")
            self.stdout.write(
                f"  * Support Contact Method: {org.get_support_contact_method_display()}")
            self.stdout.write(f"  * Support Name: {org.support_name}")
            self.stdout.write(f"  * Support Value: {org.support_value}")
            self.stdout.write(f"  * DPO Contact Method: {org.get_dpo_contact_method_display()}")
            self.stdout.write(f"  * DPO Name: {org.dpo_name}")
            self.stdout.write(f"  * DPO Value: {org.dpo_value}")

    def diagnose_settings(self):
        self.stdout.write("\n\n>> Running diagnostics on settings ...")
        if settings.DEBUG:
            self.stdout.write("\nWARNING: DEBUG is ON for this installation!")

        def print_settings(*attributes):
            for attribute in attributes:
                self.stdout.write(f"{attribute} = {getattr(settings, attribute)!r}")

        self.stdout.write("\n//INSTALLATION-WIDE SETTINGS//")

        self.stdout.write("\n# [mode]")
        print_settings("KEYCLOAK_ENABLED", "SAML2_ENABLED")

        self.stdout.write("\n# [functionality]")
        print_settings("HANDLE_DROPDOWN", "ALLOW_CONTACT_MAGENTA",
                       "ARCHIVE_TAB")

        self.stdout.write("\n# [msgraph]")
        print_settings("MSGRAPH_ALLOW_WRITE")

        self.stdout.write("\n# [logging]")
        print_settings("LOG_LEVEL")

        self.stdout.write("\n# [other]")
        print_settings()

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
                case "Problem":
                    self.diagnose_problems()
                case "DocumentReport":
                    self.diagnose_reports()
                case "OrganizationalUnit":
                    self.diagnose_units()
                case "Organization":
                    self.diagnose_organizations()
                case "Settings":
                    self.diagnose_settings()
