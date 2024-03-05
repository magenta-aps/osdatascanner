from datetime import datetime
from dateutil.tz import gettz
from parameterized import parameterized
from itertools import pairwise

from django.contrib.auth.models import User, AnonymousUser
from django.test import RequestFactory, TestCase
from django.utils.text import slugify
from django.urls import reverse_lazy

from ..adminapp.views.webscanner_views import WebScannerList
from ..adminapp.models.scannerjobs.webscanner import WebScanner
from ..adminapp.models.rules import CustomRule
from ..adminapp.views.rule_views import RuleList
from ..adminapp.views.scanner_views import StatusOverview, UserErrorLogView
from ..adminapp.models.scannerjobs.scanner import Scanner, ScanStatus
from ..adminapp.models.usererrorlog import UserErrorLog
from ..core.models import Client, Administrator
from ..organizations.models import Organization
from ..organizations.views import OrganizationListView
from .test_utilities import dummy_rule_dict


class ListViewsTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        client1 = Client.objects.create(name="client1")
        org1 = Organization.objects.create(
            name="Magenta",
            uuid="b560361d-2b1f-4174-bb03-55e8b693ad0c",
            slug=slugify("Magenta"),
            client=client1,
        )
        client2 = Client.objects.create(name="client2")
        org2 = Organization.objects.create(
            name="IANA (example.com)",
            slug=slugify("IANA (example.com)"),
            uuid="a3575dec-8d92-4266-a8d1-97b7b84817c0",
            client=client2,
        )
        dummy_rule = CustomRule.objects.create(**dummy_rule_dict)
        WebScanner.objects.create(
            name="Magenta",
            url="http://magenta.dk",
            organization=Organization.objects.get(
                uuid="b560361d-2b1f-4174-bb03-55e8b693ad0c"),
            validation_status=WebScanner.VALID,
            download_sitemap=False, rule=dummy_rule
        )
        WebScanner.objects.create(
            name="TheyDontWantYouTo",
            url="http://theydontwantyou.to",
            organization=Organization.objects.get(
                uuid="a3575dec-8d92-4266-a8d1-97b7b84817c0"),
            validation_status=WebScanner.VALID,
            download_sitemap=False,
            rule=dummy_rule
        )
        CustomRule.objects.create(name="Ny regel",
                                  organization=Organization.objects.get(
                                      uuid="b560361d-2b1f-4174-bb03-55e8b693ad0c"),
                                  description="Helt ny regel",
                                  _rule="{}"
                                  )
        CustomRule.objects.create(name="Ny regel 2",
                                  organization=Organization.objects.get(
                                      uuid="a3575dec-8d92-4266-a8d1-97b7b84817c0"),
                                  description="Helt ny regel 2",
                                  _rule="{}"
                                  )
        status = ScanStatus.objects.create(
            scan_tag={"time": datetime.now(tz=gettz()).isoformat()},
            scanner=Scanner.objects.get(name="Magenta")
        )
        ScanStatus.objects.create(
            scan_tag={"time": datetime.now(tz=gettz()).isoformat()},
            scanner=Scanner.objects.get(name="TheyDontWantYouTo")
        )

        UserErrorLog.objects.create(
            scan_status=status,
            organization=org1,
            path="The errors are here!",
            error_message="Something went awry :(",
            is_new=True
        )
        UserErrorLog.objects.create(
            scan_status=status,
            organization=org1,
            path="The errors are here!",
            error_message="ERROR ERROR ERROR",
            is_new=True
        )
        UserErrorLog.objects.create(
            scan_status=status,
            organization=org2,
            path="The errors are here!",
            error_message="OH NOOOOO!",
            is_new=True
        )
        UserErrorLog.objects.create(
            scan_status=status,
            organization=org2,
            path="The errors are here!",
            error_message="97 98 99 ... ... ... crashed",
            is_new=True
        )

    def setUp(self) -> None:
        super().setUp()
        # Every test needs access to the request factory.
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username='kjeld', email='kjeld@jensen.com', password='top_secret')

    def get_path_and_class():
        params = [
            ("WebscannerListViewTest", '/webscanners/', WebScannerList()),
            ("RuleListViewTest", '/rules/', RuleList()),
            ("ScanStatusListViewTest", '/status/', StatusOverview()),
            ("OrganizationListViewTest", '/organizations/', OrganizationListView()),
            ("UserErrorLogViewTest", '/error-log/', UserErrorLogView()),
        ]
        return params

    def test_view_as_anonymous_user(self):
        request = self.factory.get('/webscanners')
        request.user = AnonymousUser()
        response = WebScannerList.as_view()(request)
        self.assertNotEqual(response.status_code, 200)

    @parameterized.expand(get_path_and_class)
    def test_as_superuser(self, _, path, list_type):
        self.user.is_superuser = True
        qs = self.listview_get_queryset(path, list_type)
        if isinstance(list_type, RuleList):
            self.assertEqual(len(qs), 4)
        elif isinstance(list_type, OrganizationListView):
            self.assertEqual(len(qs), 2)
        elif isinstance(list_type, UserErrorLogView):
            self.assertEqual(len(qs), 4)
        else:
            self.assertEqual(len(qs), 2)

    @parameterized.expand(get_path_and_class)
    def test_as_user(self, _, path, list_type):
        qs = self.listview_get_queryset(path, list_type)
        self.assertEqual(len(qs), 0)

    @parameterized.expand(get_path_and_class)
    def test_as_administrator_for_magenta_org(self, _, path, list_type):
        administrator = Administrator.objects.create(
            user=self.user,
            client=Client.objects.get(name="client1")
        )
        qs = self.listview_get_queryset(path, list_type)
        if isinstance(list_type, UserErrorLogView):
            self.assertEqual(len(qs), 2)
        else:
            self.assertEqual(len(qs), 1)

        if isinstance(list_type, StatusOverview):
            self.assertEqual(qs.first().scanner.organization.name, "Magenta")
        elif isinstance(list_type, OrganizationListView):
            self.assertEqual(qs.first().organizations.first().name,
                             "Magenta")
        else:
            self.assertEqual(qs.first().organization.name, "Magenta")
        administrator.delete()

    @parameterized.expand(get_path_and_class)
    def test_as_administrator_for_theydontwantyouto_org(self, _, path, list_type):
        administrator = Administrator.objects.create(
            user=self.user,
            client=Client.objects.get(name="client2")
        )
        qs = self.listview_get_queryset(path, list_type)
        if isinstance(list_type, UserErrorLogView):
            self.assertEqual(len(qs), 2)
        else:
            self.assertEqual(len(qs), 1)

        if isinstance(list_type, StatusOverview):
            self.assertEqual(qs.first().scanner.organization.name,
                             "IANA (example.com)")
        elif isinstance(list_type, OrganizationListView):
            self.assertEqual(qs.first().organizations.first().name,
                             "IANA (example.com)")
        else:
            self.assertEqual(qs.first().organization.name, "IANA (example.com)")
        administrator.delete()

    def test_searching_for_scannerjobs(self):
        # Arrange
        self.user.is_superuser = True
        self.user.save()
        created_scanner = WebScanner.objects.create(
            name="obscure name",
            url="http://magenta.dk",
            organization=Organization.objects.get(
                uuid="b560361d-2b1f-4174-bb03-55e8b693ad0c"),
            validation_status=WebScanner.VALID,
            download_sitemap=False, rule=CustomRule.objects.first()
        )

        # Act
        qs = self.listview_get_queryset(
            reverse_lazy('webscanners'),
            WebScannerList(),
            request_kwargs={
                'search_field': 'obscure'})

        # Assert
        self.assertEqual(qs.count(), 1)
        self.assertEqual(qs.first(), created_scanner)

    def test_sort_usererrorlogs_default(self):
        """By default, user error logs should be sorted by pk, descending."""
        self.user.is_superuser = True
        self.user.save()

        qs = self.listview_get_queryset(
            reverse_lazy('error-log'),
            UserErrorLogView(),
            request_kwargs={})

        def is_sorted(a, b):
            return a.pk >= b.pk

        self.assertTrue(all(is_sorted(a, b) for (a, b) in pairwise(qs)))

    def test_sort_usererrorlogs_with_param(self):
        """User error logs can be sorted by giving parameters order_by and order."""
        self.user.is_superuser = True
        self.user.save()

        qs = self.listview_get_queryset(
            reverse_lazy('error-log'),
            UserErrorLogView(),
            request_kwargs={'order_by': 'error_message', 'order': 'ascending'})

        def is_sorted(a, b):
            return a.error_message <= b.error_message

        self.assertTrue(all(is_sorted(a, b) for (a, b) in pairwise(qs)))

    def test_sort_usererrorlogs_with_illegal_param(self):
        """When given an illegal sorting paramter, user error logs are sorted in the default way,
        pk descending."""
        self.user.is_superuser = True
        self.user.save()

        qs = self.listview_get_queryset(
            reverse_lazy('error-log'),
            UserErrorLogView(),
            request_kwargs={'order_by': 'organization'})

        def is_sorted(a, b):
            return a.pk >= b.pk

        self.assertTrue(all(is_sorted(a, b) for (a, b) in pairwise(qs)))

    def listview_get_queryset(self, path, view, **kwargs):
        request = self.factory.get(path, data=kwargs.get('request_kwargs'))
        request.user = self.user
        view.setup(request)
        return view.get_queryset()
