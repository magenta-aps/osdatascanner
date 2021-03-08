from django.test import RequestFactory, TestCase
from django.contrib.auth.models import User

from os2datascanner.engine2.model.ews import (
        EWSMailHandle, EWSAccountSource)
from os2datascanner.engine2.rules.regex import RegexRule, Sensitivity
from os2datascanner.engine2.pipeline import messages

from ..reportapp.management.commands import pipeline_collector
from ..reportapp.models.aliases.emailalias_model import EmailAlias
from ..reportapp.models.roles.remediator_model import Remediator
from ..reportapp.models.aliases.alias_model import Alias
from ..reportapp.models.documentreport_model import DocumentReport
from ..reportapp.models.aliasmatchrelation_model import AliasMatchRelation
from ..reportapp.views.views import MainPageView



"""Shared data"""
time0 = "2020-11-11T11:11:59+02:00"
time1 = "2020-10-28T14:21:27+01:00"

scan_tag0 = {
    "time": time0,
    "scanner": {
        "pk": 14,
        "name": "Dummy test scanner"
    },
}
scan_tag1 = {
    "scanner": {
        "pk": 11,
        "name": "Dummy test scanner2"
    },
    "time": time1
}

common_rule = RegexRule(
    expression="Vores hemmelige adgangskode er",
    sensitivity=Sensitivity.PROBLEM
)

common_rule_2 = RegexRule(
    expression="Vores hemmelige adgangskode er",
    sensitivity=Sensitivity.CRITICAL
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
    folder_name='Hundehoveder',
    entry_id=None
)

egon_scan_spec = messages.ScanSpecMessage(
        scan_tag=None,  # placeholder
        source=egon_email_handle.source,
        rule=common_rule,
        configuration={},
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
    folder_name='Indbakke',
    entry_id=None
)

kjeld_scan_spec = messages.ScanSpecMessage(
    scan_tag=None,  # placeholder
    source=kjeld_email_handle.source,
    rule=common_rule,
    configuration={},
    progress=None)

kjeld_positive_match = messages.MatchesMessage(
        scan_spec=kjeld_scan_spec._replace(scan_tag=scan_tag0),
        handle=kjeld_email_handle,
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


class MainPageViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.generate_kjeld_data()
        cls.generate_egon_data()

    @classmethod
    def generate_kjeld_data(cls):
        cls.generate_match(kjeld_positive_match)
        cls.generate_metadata(kjeld_metadata)

    @classmethod
    def generate_egon_data(cls):
        cls.generate_match(egon_positive_match)
        cls.generate_metadata(egon_metadata)

        cls.generate_match(egon_positive_match_1)
        cls.generate_metadata(egon_metadata_1)

    @classmethod
    def generate_match(cls, match):
        prev, new = pipeline_collector.get_reports_for(
            match.handle.to_json_object(),
            match.scan_spec.scan_tag)
        pipeline_collector.handle_match_message(
            prev, new, match.to_json_object())

    @classmethod
    def generate_metadata(cls, metadata):
        prev, new = pipeline_collector.get_reports_for(
            metadata.handle.to_json_object(),
            metadata.scan_tag)
        pipeline_collector.handle_metadata_message(
            new, metadata.to_json_object())

    def setUp(self):
        # Every test needs access to the request factory.
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username='kjeld', email='kjeld@jensen.com', password='top_secret')

    def test_mainpage_view_as_default_role_with_no_matches(self):
        qs = self.mainpage_get_queryset()
        self.assertEqual(len(qs), 0)

    def test_mainpage_view_with_emailalias_egon(self):
        emailalias = EmailAlias.objects.create(user=self.user, value='egon@olsen.com')
        qs = self.mainpage_get_queryset()
        self.assertEqual(len(qs), 2)
        emailalias.delete()

    def test_mainpage_view_with_emailalias_kjeld(self):
        emailalias = EmailAlias.objects.create(user=self.user, value='kjeld@jensen.com')
        qs = self.mainpage_get_queryset()
        self.assertEqual(len(qs), 1)
        emailalias.delete()

    def test_mainpage_view_with_emailaliases_egon_kjeld(self):
        emailalias = EmailAlias.objects.create(user=self.user, value='kjeld@jensen.com')
        emailalias1 = EmailAlias.objects.create(user=self.user, value='egon@olsen.com')
        qs = self.mainpage_get_queryset()
        self.assertEqual(len(qs), 3)
        emailalias.delete()
        emailalias1.delete()

    def test_mainpage_view_filter_by_scannerjob(self):
        params = '?scannerjob=14&sensitivities=all'
        emailalias = EmailAlias.objects.create(user=self.user, value='kjeld@jensen.com')
        emailalias1 = EmailAlias.objects.create(user=self.user, value='egon@olsen.com')
        qs = self.mainpage_get_queryset(params)
        self.assertEqual(len(qs), 2)
        emailalias.delete()
        emailalias1.delete()

    def test_mainpage_view_filter_by_sensitivities(self):
        params = '?scannerjob=all&sensitivities=1000'
        emailalias = EmailAlias.objects.create(user=self.user, value='kjeld@jensen.com')
        emailalias1 = EmailAlias.objects.create(user=self.user, value='egon@olsen.com')
        qs = self.mainpage_get_queryset(params)
        self.assertEqual(len(qs), 2)
        emailalias.delete()
        emailalias1.delete()

    def test_mainpage_view_filter_by_all(self):
        params = '?scannerjob=all&sensitivities=all'
        emailalias = EmailAlias.objects.create(user=self.user, value='kjeld@jensen.com')
        emailalias1 = EmailAlias.objects.create(user=self.user, value='egon@olsen.com')
        qs = self.mainpage_get_queryset(params)
        self.assertEqual(len(qs), 3)
        emailalias.delete()
        emailalias1.delete()

    def test_mainpage_view_filter_by_scannerjob_and_sensitivities(self):
        params = '?scannerjob=14&sensitivities=1000'
        emailalias = EmailAlias.objects.create(user=self.user, value='kjeld@jensen.com')
        emailalias1 = EmailAlias.objects.create(user=self.user, value='egon@olsen.com')
        qs = self.mainpage_get_queryset(params)
        self.assertEqual(len(qs), 1)
        emailalias.delete()
        emailalias1.delete()

    def test_create_alias_match_relation_on_kjeld_alias_save_and_delete(self):
        self.assertFalse(AliasMatchRelation.objects.all())
        emailalias = EmailAlias.objects.create(user=self.user, value='kjeld@jensen.com')
        self.assertTrue(AliasMatchRelation.objects.all())
        emailalias.delete()
        self.assertFalse(AliasMatchRelation.objects.all())


    def test_create_alias_match_relation_on_kjeld_documentreport_save_and_delete(self):
        emailalias = EmailAlias.objects.create(user=self.user, value='kjeld@jensen.com')
        self.assertTrue(AliasMatchRelation.objects.all())
        AliasMatchRelation.objects.all().delete()
        self.assertFalse(AliasMatchRelation.objects.all())
        report = DocumentReport.objects.get(pk=1)
        report.save()
        self.assertTrue(AliasMatchRelation.objects.all())
        emailalias.delete()
        self.assertFalse(AliasMatchRelation.objects.all())

    def mainpage_get_queryset(self, params=''):
        request = self.factory.get('/' + params)
        request.user = self.user
        view = MainPageView()
        view.setup(request)
        qs = view.get_queryset()
        return qs

    def test_mainpage_create_timestamp_when_handled_match(self):
        report = DocumentReport.objects.get(pk=self.user.pk)
        self.assertIsNone(report.resolution_time)
        report.resolution_status = 3
        report.save()
        self.assertIsNotNone(report.resolution_time)

