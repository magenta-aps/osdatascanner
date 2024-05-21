import pytest

from itertools import pairwise

from django.contrib.auth.models import AnonymousUser
from django.test import RequestFactory
from django.urls import reverse_lazy

from ..adminapp.views.webscanner_views import WebScannerList
from ..adminapp.views.rule_views import RuleList
from ..adminapp.views.scanner_views import StatusOverview, UserErrorLogView
from ..organizations.views import OrganizationListView


all_scanner_list_urls = [
        reverse_lazy('exchangescanners'),
        reverse_lazy('filescanners'),
        reverse_lazy('webscanners'),
        reverse_lazy('dropboxscanners'),
        reverse_lazy('googledrivescanners'),
        reverse_lazy('gmailscanners'),
        reverse_lazy('sbsysscanners'),
        reverse_lazy('msgraphcalendarscanner_list'),
        reverse_lazy('msgraphfilescanner_list'),
        reverse_lazy('msgraphmailscanner_list'),
    ]

path_and_class = [
            ("WebscannerListViewTest", reverse_lazy('webscanners'), WebScannerList()),
            ("RuleListViewTest", reverse_lazy('rules'), RuleList()),
            ("ScanStatusListViewTest", reverse_lazy('status'), StatusOverview()),
            ("OrganizationListViewTest", reverse_lazy('organization-list'), OrganizationListView()),
            ("UserErrorLogViewTest", reverse_lazy('error-log'), UserErrorLogView()),
        ]


def listview_get_queryset(user, path, view, **kwargs):
    request = RequestFactory().get(path, data=kwargs.get('request_kwargs'))
    request.user = user
    view.setup(request)
    return view.get_queryset()


@pytest.fixture
def populate_lists(basic_rule,
                   org_rule,
                   org2_rule,
                   web_scanner,
                   invalid_web_scanner,
                   web_scanner2,
                   basic_scanstatus,
                   web_scanstatus,
                   basic_scanstatus2,
                   test_org,
                   test_org2,
                   basic_usererrorlog,
                   basic_usererrorlog2):
    pass


@pytest.mark.django_db
class TestListViews:

    @pytest.mark.parametrize('url', all_scanner_list_urls)
    def test_view_as_anonymous_user(self, url):
        request = RequestFactory().get(url)
        request.user = AnonymousUser()
        response = WebScannerList.as_view()(request)
        assert response.status_code == 302

    @pytest.mark.parametrize('_,path,list_type', path_and_class)
    def test_as_superuser(self, _, path, list_type, superuser, populate_lists):
        qs = listview_get_queryset(superuser, path, list_type)
        if isinstance(list_type, RuleList):
            assert qs.count() == 4
        elif isinstance(list_type, OrganizationListView):
            assert qs.count() == 2
        elif isinstance(list_type, StatusOverview):
            assert qs.count() == 3
        elif isinstance(list_type, UserErrorLogView):
            assert qs.count() == 2
        elif isinstance(list_type, WebScannerList):
            assert qs.count() == 3
        else:
            raise AssertionError(f"Got unexpected list type: {list_type}")

    @pytest.mark.parametrize('_,path,list_type', path_and_class)
    def test_as_user(self, _, path, list_type, user, populate_lists):
        qs = listview_get_queryset(user, path, list_type)
        assert qs.count() == 0

    @pytest.mark.parametrize('_,path,list_type', path_and_class)
    def test_as_administrator_for_magenta_org(self, _, path, list_type, user_admin, populate_lists):
        qs = listview_get_queryset(user_admin, path, list_type)
        if isinstance(list_type, UserErrorLogView):
            assert qs.count() == 1
        elif isinstance(list_type, RuleList):
            assert qs.count() == 1
        elif isinstance(list_type, OrganizationListView):
            assert qs.count() == 1
            assert qs.first() == user_admin.administrator_for.client
        elif isinstance(list_type, StatusOverview):
            assert qs.count() == 2
            assert qs.first().scanner.organization.client == user_admin.administrator_for.client
        elif isinstance(list_type, WebScannerList):
            assert qs.count() == 2
            assert qs.first().organization.client == user_admin.administrator_for.client
        else:
            raise AssertionError(f"Got unexpected list type: {list_type}")

    @pytest.mark.parametrize('_,path,list_type', path_and_class)
    def test_as_administrator_for_other_org(self, _, path, list_type, other_admin, populate_lists):
        qs = listview_get_queryset(other_admin, path, list_type)
        if isinstance(list_type, UserErrorLogView):
            assert qs.count() == 1
        elif isinstance(list_type, RuleList):
            assert qs.count() == 1
        elif isinstance(list_type, OrganizationListView):
            assert qs.count() == 1
            assert qs.first() == other_admin.administrator_for.client
        elif isinstance(list_type, StatusOverview):
            assert qs.count() == 1
            assert qs.first().scanner.organization.client == other_admin.administrator_for.client
        elif isinstance(list_type, WebScannerList):
            assert qs.count() == 1
            assert qs.first().organization.client == other_admin.administrator_for.client
        else:
            raise AssertionError(f"Got unexpected list type: {list_type}")

    def test_searching_for_scannerjobs(self, superuser, web_scanner, invalid_web_scanner):
        # Arrange
        path = reverse_lazy('webscanners')
        view = WebScannerList()

        # Act
        qs = listview_get_queryset(
            superuser, path, view,
            request_kwargs={
                'search_field': web_scanner.name[:10]})

        # Assert
        assert qs.count() == 1
        assert qs.first() == web_scanner

    def test_sort_usererrorlogs_default(self, superuser, a_lot_of_usererrorlogs):
        """By default, user error logs should be sorted by pk, descending."""
        path = reverse_lazy('error-log')
        view = UserErrorLogView()

        qs = listview_get_queryset(
            superuser, path, view,
            request_kwargs={})

        def is_sorted(a, b):
            return a.pk >= b.pk

        assert all(is_sorted(a, b) for (a, b) in pairwise(qs))

    def test_sort_usererrorlogs_with_param(self, superuser, a_lot_of_usererrorlogs):
        """User error logs can be sorted by giving parameters order_by and order."""
        path = reverse_lazy('error-log')
        view = UserErrorLogView()

        qs = listview_get_queryset(
            superuser, path, view,
            request_kwargs={'order_by': 'error_message', 'order': 'ascending'})

        def is_sorted(a, b):
            return a.error_message <= b.error_message

        assert all(is_sorted(a, b) for (a, b) in pairwise(qs))

    def test_sort_usererrorlogs_with_illegal_param(self, superuser, a_lot_of_usererrorlogs):
        """When given an illegal sorting paramter, user error logs are sorted in the default way,
        pk descending."""

        path = reverse_lazy('error-log')
        view = UserErrorLogView()

        qs = listview_get_queryset(
            superuser, path, view,
            request_kwargs={'order_by': 'organization'})

        def is_sorted(a, b):
            return a.pk >= b.pk

        assert all(is_sorted(a, b) for (a, b) in pairwise(qs))
