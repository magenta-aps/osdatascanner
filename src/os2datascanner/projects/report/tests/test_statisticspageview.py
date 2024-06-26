import dateutil.parser
from datetime import datetime, timedelta
from typing import List, Tuple

from django.core.exceptions import PermissionDenied
from django.test import RequestFactory, TestCase, override_settings
from django.utils import timezone
from django.contrib.auth.models import User
from django.urls import reverse
from django.conf import settings

from os2datascanner.engine2.model.ews import (
        EWSMailHandle, EWSAccountSource)
from os2datascanner.engine2.rules.regex import RegexRule, Sensitivity
from os2datascanner.engine2.pipeline import messages
from os2datascanner.engine2.utilities.datetime import parse_datetime
from os2datascanner.core_organizational_structure.models.position import Role

from ...report.organizations.models import (
    Account, Organization, OrganizationalUnit, Position, Alias)
from ..reportapp.models.documentreport import DocumentReport
from ..reportapp.views.statistics_views import (
        UserStatisticsPageView, LeaderStatisticsPageView,
        DPOStatisticsPageView, DPOStatisticsCSVView)
from ..reportapp.utils import iterate_queryset_in_batches, create_alias_and_match_relations

from .generate_test_data import record_match, record_metadata


"""Shared data"""
time0 = "2020-11-11T11:11:59+02:00"
time1 = "2020-10-28T14:21:27+01:00"
time2 = "2020-09-22T04:07:12+03:00"

org_frag = messages.OrganisationFragment(
    name="Statistics Test Corp.", uuid="d92ff0c9-f066-40dc-a57e-541721b6c23e")

scan_tag0 = messages.ScanTagFragment(
        time=parse_datetime(time0),
        scanner=messages.ScannerFragment(pk=14, name="Dummy test scanner"),
        user=None, organisation=org_frag)

scan_tag1 = messages.ScanTagFragment(
        time=parse_datetime(time1),
        scanner=messages.ScannerFragment(pk=11, name="Dummy test scanner2"),
        user=None, organisation=org_frag)

scan_tag2 = messages.ScanTagFragment(
        time=parse_datetime(time2),
        scanner=messages.ScannerFragment(pk=17, name="Dummy test scanner3"),
        user=None, organisation=org_frag)

common_rule = RegexRule(
    expression="Vores hemmelige adgangskode er",
    sensitivity=Sensitivity.PROBLEM
)

common_rule_2 = RegexRule(
    expression="Vores hemmelige adgangskode er",
    sensitivity=Sensitivity.CRITICAL
)

common_rule_3 = RegexRule(
    expression="Vores hemmelige adgangskode er",
    sensitivity=Sensitivity.WARNING
)

"""EGON DATA"""
egon_email_handle = EWSMailHandle(
    source=EWSAccountSource(
        domain='@olsen.com',
        server=None,
        admin_user=None,
        admin_password=None,
        user='egon'),
    path='TDJHGFIHDIJHSKJGHKFUGIUHIUEHIIHE',
    mail_subject='Jeg har en plan',
    folder_name='Hundehoveder',
    entry_id=None
)

egon_email_handle_1 = EWSMailHandle(
    source=EWSAccountSource(
        domain='@olsen.com',
        server=None,
        admin_user=None,
        admin_password=None,
        user='egon'),
    path='DLFIGHDSLUJKGFHEWIUTGHSLJHFGBSVDKJFHG',
    mail_subject='TI STILLE SINDSSYGE KVINDEMENNESKE!',
    folder_name='Fnatmider',
    entry_id=None
)

egon_scan_spec = messages.ScanSpecMessage(
        scan_tag=None,  # placeholder
        source=egon_email_handle.source,
        rule=common_rule,
        configuration={},
        filter_rule=None,
        progress=None)

egon_positive_match = messages.MatchesMessage(
        scan_spec=egon_scan_spec._replace(scan_tag=scan_tag0),
        handle=egon_email_handle,
        matched=True,
        matches=[messages.MatchFragment(
                rule=common_rule_2,
                matches=[{"dummy": "match object"}])]
)

egon_positive_match_1 = messages.MatchesMessage(
        scan_spec=egon_scan_spec._replace(scan_tag=scan_tag1),
        handle=egon_email_handle_1,
        matched=True,
        matches=[messages.MatchFragment(
                rule=common_rule_2,
                matches=[{"dummy": "match object"}])]
)

egon_metadata = messages.MetadataMessage(
    scan_tag=scan_tag0,
    handle=egon_email_handle,
    metadata={"email-account": "egon@olsen.com"}
)

egon_metadata_1 = messages.MetadataMessage(
    scan_tag=scan_tag1,
    handle=egon_email_handle_1,
    metadata={"email-account": "egon@olsen.com"}
)


"""KJELD DATA"""
kjeld_email_handle = EWSMailHandle(
    source=EWSAccountSource(
        domain='@jensen.com',
        server=None,
        admin_user=None,
        admin_password=None,
        user='kjeld'),
    path='TDJHGFIHDIJHSKJGHKFUGIUHIUEHIIHE',
    mail_subject='Er det farligt?',
    folder_name='Favorit',
    entry_id=None
)

kjeld_email_handle_1 = EWSMailHandle(
    source=EWSAccountSource(
        domain='@jensen.com',
        server=None,
        admin_user=None,
        admin_password=None,
        user='kjeld'),
    path='ASDGYSDFSDFSDFDSFDFSASD',
    mail_subject='Hvad skal jeg sige til Yvonne?',
    folder_name='Indbakke',
    entry_id=None
)

kjeld_scan_spec = messages.ScanSpecMessage(
    scan_tag=None,  # placeholder
    source=kjeld_email_handle.source,
    rule=common_rule,
    configuration={},
    filter_rule=None,
    progress=None)

kjeld_positive_match = messages.MatchesMessage(
        scan_spec=kjeld_scan_spec._replace(scan_tag=scan_tag0),
        handle=kjeld_email_handle,
        matched=True,
        matches=[messages.MatchFragment(
                rule=common_rule,
                matches=[{"dummy": "match object"}])]
)

kjeld_positive_match_1 = messages.MatchesMessage(
        scan_spec=kjeld_scan_spec._replace(scan_tag=scan_tag2),
        handle=kjeld_email_handle_1,
        matched=True,
        matches=[messages.MatchFragment(
                rule=common_rule,
                matches=[{"dummy": "match object"}])]
)

kjeld_metadata = messages.MetadataMessage(
    scan_tag=scan_tag0,
    handle=kjeld_email_handle,
    metadata={"email-account": "kjeld@jensen.com"}
)

kjeld_metadata_1 = messages.MetadataMessage(
    scan_tag=scan_tag2,
    handle=kjeld_email_handle_1,
    metadata={"email-account": "kjeld@jensen.com"}
)

"""BENNY DATA"""
benny_email_handle = EWSMailHandle(
    source=EWSAccountSource(
        domain='@frandsen.com',
        server=None,
        admin_user=None,
        admin_password=None,
        user='benny'),
    path='HJKFHSDJKFDFKSLASDGHJ',
    mail_subject="Du' smælderfed mand!",
    folder_name='Vigtigt',
    entry_id=None
)

benny_email_handle_1 = EWSMailHandle(
    source=EWSAccountSource(
        domain='@frandsen.com',
        server=None,
        admin_user=None,
        admin_password=None,
        user='benny'),
    path='HJKFHSDJKFDFKSLASDGHJ',
    mail_subject="Så så Kjeld, det var jo ikke sådan ment",
    folder_name='Spam',
    entry_id=None
)

benny_scan_spec = messages.ScanSpecMessage(
    scan_tag=None,  # placeholder
    source=benny_email_handle.source,
    rule=common_rule,
    configuration={},
    filter_rule=None,
    progress=None)

benny_positive_match = messages.MatchesMessage(
        scan_spec=benny_scan_spec._replace(scan_tag=scan_tag0),
        handle=benny_email_handle,
        matched=True,
        matches=[messages.MatchFragment(
                rule=common_rule_2,
                matches=[{"dummy": "match object"}])]
)

benny_positive_match_1 = messages.MatchesMessage(
        scan_spec=benny_scan_spec._replace(scan_tag=scan_tag1),
        handle=benny_email_handle_1,
        matched=True,
        matches=[messages.MatchFragment(
                rule=common_rule_3,
                matches=[{"dummy": "match object"}])]
)

benny_metadata = messages.MetadataMessage(
    scan_tag=scan_tag0,
    handle=benny_email_handle,
    metadata={"email-account": "benny@frandsen.com"}
)

benny_metadata_1 = messages.MetadataMessage(
    scan_tag=scan_tag1,
    handle=benny_email_handle_1,
    metadata={"email-account": "benny@frandsen.com"}
)

"""YVONNE DATA"""
yvonne_email_handle = EWSMailHandle(
    source=EWSAccountSource(
        domain='@jensen.com',
        server=None,
        admin_user=None,
        admin_password=None,
        user='yvonne'),
    path='SDFYSDFUYSDFIUASDM;AMSD',
    mail_subject='Los fiskos, los salatos, los kotelettos, los vinos blancos og Los Coca Colos',
    folder_name='Spanien',
    entry_id=None
)

yvonne_scan_spec = messages.ScanSpecMessage(
    scan_tag=None,  # placeholder
    source=yvonne_email_handle.source,
    rule=common_rule,
    configuration={},
    filter_rule=None,
    progress=None)

yvonne_positive_match = messages.MatchesMessage(
        scan_spec=yvonne_scan_spec._replace(scan_tag=scan_tag0),
        handle=yvonne_email_handle,
        matched=True,
        matches=[messages.MatchFragment(
                rule=common_rule_2,
                matches=[{"dummy": "match object"}])]
)

yvonne_metadata = messages.MetadataMessage(
    scan_tag=scan_tag0,
    handle=yvonne_email_handle,
    metadata={"email-account": "yvonne@jensen.com"}
)


class StatisticsPageViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        Organization.objects.create(
            name="Statistics Test Corp.",
            uuid='d92ff0c9-f066-40dc-a57e-541721b6c23e')
        cls.generate_kjeld_data()
        cls.generate_egon_data()
        cls.generate_yvonne_data()
        cls.generate_benny_data()

    @classmethod
    def generate_kjeld_data(cls):
        record_match(kjeld_positive_match)
        record_metadata(kjeld_metadata)

        record_match(kjeld_positive_match_1)
        record_metadata(kjeld_metadata_1)

    @classmethod
    def generate_egon_data(cls):
        record_match(egon_positive_match)
        record_metadata(egon_metadata)

        record_match(egon_positive_match_1)
        record_metadata(egon_metadata_1)

    @classmethod
    def generate_yvonne_data(cls):
        record_match(yvonne_positive_match)
        record_metadata(yvonne_metadata)

    @classmethod
    def generate_benny_data(cls):
        record_match(benny_positive_match)
        record_metadata(benny_metadata)

        record_match(benny_positive_match_1)
        record_metadata(benny_metadata_1)

    def setUp(self):
        self.org = Organization.objects.get(
            name="Statistics Test Corp.",
            uuid='d92ff0c9-f066-40dc-a57e-541721b6c23e')

        self.olsen_banden = OrganizationalUnit.objects.create(
            name="Olsen Banden", organization=Organization.objects.first())

        # Every test needs access to the request factory.
        self.factory = RequestFactory()
        self.kjeld_account = Account.objects.create(
                username="kjeld",
                organization=self.org)
        self.egon_account = Account.objects.create(
                username="egon",
                organization=self.org)
        self.yvonne_account = Account.objects.create(
                username="yvonne",
                organization=self.org)
        self.benny_account = Account.objects.create(
                username="benny",
                organization=self.org)

        # AccountManager (above) takes care of creating corresponding User objects.
        # Assign them for use later here.
        self.kjeld = User.objects.get(username="kjeld")
        self.egon = User.objects.get(username="egon")
        self.yvonne = User.objects.get(username="yvonne")
        self.benny = User.objects.get(username="benny")

        # Create aliases for the accounts
        self.kjeld_alias = Alias.objects.create(
            user=self.kjeld,
            account=self.kjeld_account,
            _alias_type='email',
            _value='kjeld@jensen.com')
        self.egon_alias = Alias.objects.create(
            user=self.egon,
            account=self.egon_account,
            _alias_type='email',
            _value='egon@olsen.com')
        self.yvonne_alias = Alias.objects.create(
            user=self.yvonne,
            account=self.yvonne_account,
            _alias_type='email',
            _value='yvonne@jensen.com')
        self.benny_alias = Alias.objects.create(
            user=self.benny,
            account=self.benny_account,
            _alias_type='email',
            _value='benny@frandsen.com')

        create_alias_and_match_relations(self.kjeld_alias)
        create_alias_and_match_relations(self.egon_alias)
        create_alias_and_match_relations(self.yvonne_alias)
        create_alias_and_match_relations(self.benny_alias)

        settings.DPO_CSV_EXPORT = True

    def test_own_userstatisticspage_without_privileges(self):
        """A User with an Account can see their personal statistics."""
        response = self.get_user_statisticspage_response(user=self.benny)
        self.assertEqual(
                response.status_code,
                200,
                "normal user cannot access own statistics")

    def test_other_userstatisticspage_without_privileges(self):
        """A User with an Account can't see the statistics of an unrelated
        user."""
        with self.assertRaises(PermissionDenied):
            self.get_user_statisticspage_response(
                    user=self.benny, pk=self.yvonne_account.pk)

    def test_leader_statisticspage_as_manager(self):
        """A user with a 'manager'-position to an organizational unit should
        be able to access the leader overview page."""

        Position.objects.create(account=self.yvonne_account, unit=self.olsen_banden, role="manager")

        response = self.get_leader_statisticspage_response(self.yvonne)

        self.assertEqual(
            response.status_code,
            200,
            "A user with a manager-position cannot access the leader overview.")

    def test_leader_statisticspage_as_superuser(self):
        """A superuser should be able to access the leader overview page."""
        self.egon.is_superuser = True
        self.egon.save()

        response = self.get_leader_statisticspage_response(self.egon)

        self.assertEqual(
            response.status_code,
            200,
            "A superuser cannot access the leader overview.")

    def test_leader_statisticspage_with_no_privileges(self):
        """A user with no privileges should not be able to access the leader
        overview page."""

        response = self.get_leader_statisticspage_response(self.benny)

        self.assertEqual(response.status_code, 403)

    # created_timestamp
    def test_statisticspage_created_timestamp_as_dpo(self):
        Position.objects.create(account=self.kjeld_account, unit=self.olsen_banden, role=Role.DPO)
        view = self.get_statisticspage_object()
        created_timestamp = view.matches[0].get('created_month')
        now = timezone.now().date()

        self.assertEqual(created_timestamp, timezone.datetime(now.year, now.month, 1).date())

    # count_new_matches_by_month()
    def test_statisticspage_count_new_matches_by_month_as_dpo(self):
        Position.objects.create(account=self.kjeld_account, unit=self.olsen_banden, role=Role.DPO)

        # Overrides timestamps static dates and saves the old ones
        original_timestamps = static_timestamps()

        view = self.get_statisticspage_object()

        _, _, _, view.created_month, view.resolved_month = view.make_data_structures(view.matches)
        test_date = dateutil.parser.parse("2020-11-28T14:21:59+05:00")

        self.assertListEqual(view.count_new_matches_by_month(test_date),
                             [['Dec 2019', 0], ['Jan 2020', 0], ['Feb 2020', 0],
                              ['Mar 2020', 0], ['Apr 2020', 0], ['Maj 2020', 0],
                              ['Jun 2020', 0], ['Jul 2020', 0], ['Aug 2020', 0],
                              ['Sep 2020', 1], ['Okt 2020', 2], ['Nov 2020', 4]])

        # Reset to old values
        reset_timestamps(original_timestamps)

    def test_statisticspage_count_new_matches_by_month_old_matches_as_dpo(self):

        Position.objects.create(account=self.kjeld_account, unit=self.olsen_banden, role=Role.DPO)

        # Overrides timestamps static dates and saves the old ones
        original_timestamps = static_timestamps()

        view = self.get_statisticspage_object()

        _, _, _, view.created_month, view.resolved_month = view.make_data_structures(view.matches)
        test_date = dateutil.parser.parse("2021-09-28T14:21:59+05:00")

        self.assertListEqual(view.count_new_matches_by_month(test_date),
                             [['Okt 2020', 2], ['Nov 2020', 4], ['Dec 2020', 0],
                              ['Jan 2021', 0], ['Feb 2021', 0], ['Mar 2021', 0],
                              ['Apr 2021', 0], ['Maj 2021', 0], ['Jun 2021', 0],
                              ['Jul 2021', 0], ['Aug 2021', 0], ['Sep 2021', 0]])

        # Reset to old values
        reset_timestamps(original_timestamps)

    def test_statisticspage_count_unhandled_matches_by_month(self):
        Position.objects.create(account=self.kjeld_account, unit=self.olsen_banden, role=Role.DPO)

        # Saves old timestamps and overrides
        original_created_timestamps = static_timestamps('created_timestamp')
        original_resolution_time = static_timestamps('resolution_time')

        view = self.get_statisticspage_object()

        _, _, _, view.created_month, view.resolved_month = view.make_data_structures(view.matches)

        test_date = dateutil.parser.parse("2021-4-28T14:21:59+05:00")

        self.assertListEqual(view.count_unhandled_matches_by_month(test_date),
                             [['Maj 2020', 0], ['Jun 2020', 0], ['Jul 2020', 0],
                              ['Aug 2020', 0], ['Sep 2020', 1], ['Okt 2020', 3],
                              ['Nov 2020', 7], ['Dec 2020', 7], ['Jan 2021', 7],
                              ['Feb 2021', 7], ['Mar 2021', 0], ['Apr 2021', 0]])

        # Resets back to old values
        reset_timestamps(original_created_timestamps, 'created_timestamp')
        reset_timestamps(original_resolution_time, 'resolution_time')

    def test_filter_by_scannerjob(self):
        """Filtering by scannerjob should only return the reports associated
        with a specific scannerjob."""
        Position.objects.create(account=self.egon_account, unit=self.olsen_banden, role=Role.DPO)

        response11 = self.get_dpo_statisticspage_response(self.egon, params='?scannerjob=11')
        response14 = self.get_dpo_statisticspage_response(self.egon, params='?scannerjob=14')
        response17 = self.get_dpo_statisticspage_response(self.egon, params='?scannerjob=17')

        # There are 2 reports from scanner job 11
        self.assertEqual(response11.context_data.get('scannerjobs')[-1], "11")
        self.assertEqual(response11.context_data.get('match_data').get('unhandled').get('count'), 2)

        # There are 4 reports from scanner job 14
        self.assertEqual(response14.context_data.get('scannerjobs')[-1], "14")
        self.assertEqual(response14.context_data.get('match_data').get('unhandled').get('count'), 4)

        # There are 1 reports from scanner job 17
        self.assertEqual(response17.context_data.get('scannerjobs')[-1], "17")
        self.assertEqual(response17.context_data.get('match_data').get('unhandled').get('count'), 1)

    def test_filter_by_orgunit(self):
        """Filtering by organizational units should only return results from
        users with employee positions in that unit."""
        kun_egon = OrganizationalUnit.objects.create(
            name='Kun Egon',
            organization=self.org)

        # Add accounts to the OUs
        self.egon_account.units.add(self.olsen_banden, kun_egon)
        self.benny_account.units.add(self.olsen_banden)
        self.kjeld_account.units.add(self.olsen_banden)

        Position.dpos.create(account=self.egon_account, unit=self.olsen_banden)
        Position.dpos.create(account=self.egon_account, unit=kun_egon)

        response_ob = self.get_dpo_statisticspage_response(
            self.egon, params=f'?orgunit={str(self.olsen_banden.uuid)}')
        response_ke = self.get_dpo_statisticspage_response(
            self.egon, params=f'?orgunit={str(kun_egon.uuid)}')

        self.assertEqual(response_ob.context_data.get('orgunits')
                         [-1], str(self.olsen_banden.uuid))
        self.assertEqual(response_ob.context_data.get(
            'match_data').get('unhandled').get('count'), 6)

        self.assertEqual(response_ke.context_data.get('orgunits')
                         [-1], str(kun_egon.uuid))
        self.assertEqual(response_ke.context_data.get(
            'match_data').get('unhandled').get('count'), 2)

    def test_filter_by_orgunit_with_multiple_positions(self):
        # Arrange
        Position.objects.create(
            account=self.egon_account, unit=self.olsen_banden, role=Role.DPO)
        Position.objects.create(
            account=self.egon_account, unit=self.olsen_banden, role=Role.EMPLOYEE)

        # Act
        response_ob = self.get_dpo_statisticspage_response(
              self.egon, params=f'?orgunit={str(self.olsen_banden.uuid)}')

        # Assert
        self.assertEqual(response_ob.context_data.get(
           'match_data').get('unhandled').get('count'), 2)

    def test_access_from_different_organization(self):
        """A user should only be able to see results from their own organization."""
        marvel = Organization.objects.create(name="Marvel Cinematic Universe")
        avengers = OrganizationalUnit.objects.create(name="The Avengers", organization=marvel)
        Account.objects.create(
            username='the_hulk',
            first_name='Bruce',
            last_name='Banner',
            organization=marvel)
        hulk = User.objects.get(username='the_hulk')
        Position.objects.create(account=hulk.account, unit=avengers, role=Role.DPO)

        response = self.get_dpo_statisticspage_response(hulk)

        self.assertEqual(response.context_data.get('match_data').get('unhandled').get('count'), 0)

    @override_settings(LANGUAGE_CODE='en-US', LANGUAGES=(('en', 'English'),))
    def test_dpo_with_access_to_csv_export(self):
        """A dpo should be able to export data from their own orgunit."""

        self.egon_account.units.add(self.olsen_banden)
        self.benny_account.units.add(self.olsen_banden)

        Position.dpos.create(account=self.egon_account, unit=self.olsen_banden)

        response = self.get_dpo_statistics_csv_response(
            self.egon, params=f'?orgunit={str(self.olsen_banden.uuid)}')
        Headers, _line1, line2, *_ = response.streaming_content

        self.assertIn("unhandled,4", str(line2), "Data doesn't contain 2 matches")

    def test_dpo_without_access_to_csv_export(self):
        """A dpo shouldn't be able to export data from another orgunit."""

        kun_egon = OrganizationalUnit.objects.create(
            name='Kun Egon',
            organization=self.org)
        self.egon_account.units.add(kun_egon, self.olsen_banden)
        Position.objects.create(account=self.egon_account, unit=kun_egon, role=Role.DPO)

        with self.assertRaises(OrganizationalUnit.DoesNotExist):
            self.get_dpo_statistics_csv_response(
                self.egon, params=f'?orgunit={str(self.olsen_banden.uuid)}')

    def test_csv_export_without_privileges(self):
        """A user with no privileges should not be able to export dpo data,
        and should instead be redirected to main page."""

        response = self.get_dpo_statistics_csv_response(self.benny)

        self.assertEqual(response.status_code, 302)

    def test_csv_export_feature_flag(self):
        """When the feature flag DPO_CSV_EXPORT is off,
        a user should be met with PermissionDenied."""

        settings.DPO_CSV_EXPORT = False

        with self.assertRaises(PermissionDenied):
            self.get_dpo_statistics_csv_response(self.egon)

    @override_settings(LANGUAGE_CODE='en-US', LANGUAGES=(('en', 'English'),))
    def test_csv_export_single_scannerjob(self):
        """Exporting data from a single scannerjob, should only yield data from that scannerjob."""

        Position.objects.create(account=self.egon_account, unit=self.olsen_banden, role=Role.DPO)

        response = self.get_dpo_statistics_csv_response(self.egon, params='?scannerjob=11')
        Headers, _line1, line2, *_ = response.streaming_content

        self.assertIn("unhandled,2", str(line2), "Data doesn't contain 2 matches")

    @override_settings(LANGUAGE_CODE='en-US', LANGUAGES=(('en', 'English'),))
    def test_csv_export_scannerjob_and_orgunit_filter(self):
        """Exporting data from an orgunit and scannerjob, should only contain relevant data."""

        self.egon_account.units.add(self.olsen_banden)

        Position.dpos.create(account=self.egon_account, unit=self.olsen_banden)

        response = self.get_dpo_statistics_csv_response(
            self.egon, params=f"?scannerjob=11&orgunit={str(self.olsen_banden.uuid)}")
        Headers, _line1, line2, *_ = response.streaming_content

        self.assertIn("unhandled,1", str(line2), "Data doesn't contain 1 matches")

    @override_settings(LANGUAGE_CODE='en-US', LANGUAGES=(('en', 'English'),))
    def test_superuser_export_entire_organization(self):
        """A superuser should be able to export data for their entire organization."""
        self.egon.is_superuser = True

        explicit = self.get_dpo_statistics_csv_response(self.egon, params="?orgunit=all")
        implicit = self.get_dpo_statistics_csv_response(self.egon)

        Headers, _line1, line2_ex, *_ = explicit.streaming_content
        Headers, _line1, line2_im, *_ = implicit.streaming_content

        self.assertIn("unhandled,7", str(line2_ex))
        self.assertIn("unhandled,7", str(line2_im))

    @override_settings(LANGUAGE_CODE='en-US', LANGUAGES=(('en', 'English'),))
    def test_dpo_export_entire_organization(self):
        """A dpo should be able to export data for their entire organization."""
        Position.objects.create(account=self.egon_account, unit=self.olsen_banden, role=Role.DPO)

        explicit = self.get_dpo_statistics_csv_response(self.egon, params="?orgunit=all")
        implicit = self.get_dpo_statistics_csv_response(self.egon)

        Headers, _line1, line2_ex, *_ = explicit.streaming_content
        Headers, _line1, line2_im, *_ = implicit.streaming_content

        self.assertIn("unhandled,7", str(line2_ex))
        self.assertIn("unhandled,7", str(line2_im))

    # StatisticsPageView()
    def get_statisticspage_object(self):
        # XXX: we don't use request for anything! Is this deliberate?
        # request = self.factory.get('/statistics')
        # request.user = self.kjeld
        view = DPOStatisticsPageView()
        return view

    def get_user_statisticspage_response(self, user, **kwargs):
        request = self.factory.get('/statistics/view/')
        request.user = user
        return UserStatisticsPageView.as_view()(request, **kwargs)

    # StatisticsPageView()
    def get_leader_statisticspage_object(self):
        # XXX: we don't use request for anything! Is this deliberate?
        # request = self.factory.get('/statistics/leader')
        # request.user = self.kjeld
        view = LeaderStatisticsPageView()
        return view

    def get_leader_statisticspage_response(self, user, **kwargs):
        request = self.factory.get(reverse('statistics-leader'))
        request.user = user
        return LeaderStatisticsPageView.as_view()(request, **kwargs)

    def get_dpo_statisticspage_response(self, user, params='', **kwargs):
        request = self.factory.get(reverse('statistics-dpo') + params)
        request.user = user
        return DPOStatisticsPageView.as_view()(request, **kwargs)

    def get_dpo_statistics_csv_response(self, user, params='', **kwargs):
        request = self.factory.get(reverse('statistics-dpo-export') + params)
        request.user = user
        return DPOStatisticsCSVView.as_view()(request, **kwargs)


# Helper functions
# Overrides timestamps to have static data
def static_timestamps(time_type: str = 'created_timestamp',
                      added_days: int = 0) -> List[Tuple[int, datetime]]:
    original_timestamps = []

    if time_type == 'created_timestamp':  # Default
        for match in DocumentReport.objects.all():
            original_timestamps.append((match.pk, match.created_timestamp))
            match.created_timestamp = match.scan_time + timedelta(days=added_days)
            match.save()

    elif time_type == 'resolution_time':
        for batch in iterate_queryset_in_batches(10000, DocumentReport.objects.all()):
            for match in batch:
                original_timestamps.append((match.pk, match.resolution_time))
                match.resolution_status = 3
                match.resolution_time = dateutil.parser.parse("2021-3-28T14:21:59+05:00")
            DocumentReport.objects.bulk_update(batch, ['resolution_status', 'resolution_time'])
    else:
        print("Typo in argument 'time_type' in static_timestamps()")

    return original_timestamps


# Reset to old values
def reset_timestamps(arg: List[Tuple[int, datetime]],  # noqa: CCR001, E501 too high cognitive complexity
                     time_type: str = 'created_timestamp'):

    if time_type == 'created_timestamp':  # Default
        for match in DocumentReport.objects.all():
            for a in arg:
                if a[0] == match.pk:
                    match.created_timestamp = a[1]
            match.save()

    elif time_type == 'resolution_time':
        for match in DocumentReport.objects.all():
            for a in arg:
                if a[0] == match.pk:
                    match.resolution_status = None
                    match.resolution_time = a[1]
            match.save()

    else:
        print("Typo in argument 'time_type' in reset_timestamps()")
