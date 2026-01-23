import random
from datetime import datetime
from faker import Faker
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from django.contrib.auth.models import User

from os2datascanner.core_organizational_structure.models.aliases import AliasType
from os2datascanner.projects.report.reportapp.models.documentreport import DocumentReport
from os2datascanner.projects.report.organizations.models.organization import Organization
from os2datascanner.projects.report.organizations.models.account import Account
from os2datascanner.projects.report.organizations.models.aliases import Alias
from os2datascanner.projects.report.reportapp.models.scanner_reference import ScannerReference
from os2datascanner.engine2.rules.cpr import CPRRule
from os2datascanner.engine2.model.file import FilesystemHandle
from os2datascanner.engine2.rules.rule import Sensitivity


class Command(BaseCommand):
    help = 'Generates test data for DocumentReport objects.'

    def add_arguments(self, parser):
        parser.add_argument(
            'count', type=int, help='The number of DocumentReports to create.')
        parser.add_argument(
            '--username',
            type=str,
            help='Username of an existing Account to associate reports with.')
        parser.add_argument(
            '--org-name',
            type=str,
            help='The name of the organization to use. Required if more than '
                 'one organization exists and --username is not provided.')

    def handle(self, *args, **options):
        count = options['count']
        username = options['username']
        org_name = options['org_name']
        fake = Faker()

        organization, user_alias = self._get_organization_and_alias(
            username, org_name)

        aliases_to_relate = [user_alias] if user_alias else self._get_remediator_aliases()

        self.stdout.write(f'Creating {count} DocumentReport objects...')

        scanner_pk = random.randint(100001, 200000)
        while ScannerReference.objects.filter(scanner_pk=scanner_pk).exists():
            scanner_pk = random.randint(100001, 200000)

        scanner_reference = ScannerReference.objects.create(
            scanner_pk=scanner_pk,
            scanner_name=f"Filescanner {scanner_pk}",
            organization=organization,
        )

        reports_to_create = []
        for i in range(count):
            file_path = fake.file_path(depth=5, absolute=True)
            handle = FilesystemHandle.make_handle(path=file_path)
            rule = CPRRule(name="CPR")

            num_matches = random.randint(1, 5)
            matches_list = []
            for _ in range(num_matches):
                cpr_number = "1111111118"
                partially_censored_cpr = cpr_number[:6] + '-XXXX'
                fully_censored_cpr = 'XXXXXX-XXXX'

                paragraph = fake.paragraph(nb_sentences=3)
                words = paragraph.split(' ')
                insert_position = random.randint(0, len(words))
                words.insert(insert_position, fully_censored_cpr)
                context_with_match = ' '.join(words)

                matches_list.append({
                    "value": cpr_number,
                    "offset": random.randint(0, 100),
                    "match": partially_censored_cpr,
                    "context": context_with_match,
                })

            scan_tag = {
                "time": datetime.now().isoformat(),
                "user": f"test_user_{i}",
                "scanner": {
                    "pk": scanner_reference.scanner_pk,
                    "name": scanner_reference.scanner_name,
                    "test": True, "keep_fp": False},
                "organisation": {
                    "name": organization.name,
                    "uuid": str(organization.uuid)}
            }

            scan_spec = {
                "scan_tag": scan_tag,
                "source": handle.source.to_json_object(),
                "rule": rule.to_json_object(),
                "configuration": {}, "filter_rule": None, "progress": None,
                "explorer_queue": "os2ds_scan_specs",
                "conversion_queue": "os2ds_conversions",
            }

            raw_matches = {
                "scan_spec": scan_spec,
                "handle": handle.to_json_object(),
                "matched": True,
                "matches": [{"rule": rule.to_json_object(), "matches": matches_list}]
            }

            naive_datetime = fake.date_time_this_decade()
            aware_datetime = timezone.make_aware(naive_datetime, timezone.get_current_timezone())

            reports_to_create.append(
                DocumentReport(
                    scanner_job=scanner_reference,
                    path=file_path,
                    scan_time=timezone.now(),
                    created_timestamp=timezone.now(),
                    datasource_last_modified=aware_datetime,
                    source_type='smbc',
                    sensitivity=random.choice(list(Sensitivity)).value,
                    probability=random.random(),
                    owner=fake.user_name(),
                    raw_matches=raw_matches,
                    number_of_matches=num_matches,
                    sort_key=handle.sort_key,
                )
            )

        created_reports = DocumentReport.objects.bulk_create(reports_to_create)

        if aliases_to_relate:
            self._bulk_create_alias_relations(created_reports, aliases_to_relate)

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created {count} DocumentReport objects.'))

    def _get_organization_and_alias(self, username, org_name):
        user_alias = None
        if username:
            try:
                user = User.objects.get(username=username)
                account = Account.objects.get(user=user)
                user_alias = Alias.objects.filter(account=account).first()
                if not user_alias:
                    raise CommandError(f"No alias found for user '{username}'.")
                return account.organization, user_alias
            except User.DoesNotExist:
                raise CommandError(f"User with username '{username}' not found.")
            except Account.DoesNotExist:
                raise CommandError(f"Account for user '{username}' not found.")

        if org_name:
            try:
                return Organization.objects.get(name=org_name), None
            except Organization.DoesNotExist:
                raise CommandError(f"Organization with name '{org_name}' not found.")

        orgs = Organization.objects.all()
        if orgs.count() == 0:
            raise CommandError("No organizations found. Please create one first.")
        if orgs.count() > 1:
            raise CommandError(
                "More than one organization exists. Please specify one with "
                "--org-name or provide a --username.")
        return orgs.first(), None

    def _get_remediator_aliases(self):
        aliases = list(
            Alias.objects.filter(_value='0', _alias_type=AliasType.REMEDIATOR)
        )
        if not aliases:
            self.stdout.write(self.style.WARNING(
                "No universal remediator aliases found. Reports will be "
                "created without alias relations."))
        return aliases

    def _bulk_create_alias_relations(self, reports, aliases):
        ThroughModel = DocumentReport.alias_relations.through
        relations_to_create = []
        for report in reports:
            for alias in aliases:
                relations_to_create.append(
                    ThroughModel(documentreport_id=report.pk, alias_id=alias.pk)
                )
        if relations_to_create:
            ThroughModel.objects.bulk_create(relations_to_create)
