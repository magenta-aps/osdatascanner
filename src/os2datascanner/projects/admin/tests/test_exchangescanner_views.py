
import pytest

from django.test import RequestFactory
from django.urls.base import reverse

from django.core.files.uploadedfile import SimpleUploadedFile

from ..adminapp.views.exchangescanner_views import (
    ExchangeScannerCopy, ExchangeScannerCreate, ExchangeScannerUpdate)


def get_exchangescanner_response(user):
    request = RequestFactory().get('/exchangescanners/add/')
    request.user = user
    response = ExchangeScannerCreate.as_view()(request)
    return response


@pytest.mark.django_db
class TestExchangeScannerViews:

    def test_exchangesscanner_org_units_list_as_administrator(
            self,
            user_admin,
            familien_sand,
            nisserne,
            bingoklubben,
            nørre_snede_if,
            kok_sokker,
            olsen_banden):
        """Note that this is not a django administrator role,
        but instead an organization administrator."""
        response = get_exchangescanner_response(user_admin)

        tree_queryset = response.context_data['org_units']

        expected_order = [bingoklubben, familien_sand, kok_sokker, nisserne, nørre_snede_if]

        assert len(tree_queryset) == 5
        assert list(tree_queryset) == expected_order
        assert olsen_banden not in tree_queryset

    # TODO: Figure out why client is not updated in database and make unit test pass
    # def test_exchangesscanner_org_units_list_viewable_as_administrator(self):
    #     """Testcase for testing if ldap feature flags are complied with."""
    #     admin = Administrator.objects.create(
    #         user=self.kjeld,
    #         client=Client.objects.get(name="client1"),
    #     )
    #     # Check if is possible NOT to choose an org. unit.
    #     response = self.get_exchangescanner_response()
    #     response.render()
    #     self.assertNotIn(str(response.content), 'sel_1')
    #
    #     features = 0
    #     features += (1 << 0)
    #     features += (1 << 1)
    #     features += (1 << 2)
    #     client1 = Client.objects.get(name='client1')
    #     client1.features = features
    #     client1.save()
    #     # Check if is possible to choose an org. unit.
    #     response1 = self.get_exchangescanner_response()
    #     self.assertIn(str(response1.content), 'sel_1')
    #
    #     client1.features = 0
    #     client1.save()
    #     admin.delete()

    def test_exchangescanner_org_units_list_as_superuser(
            self, superuser, familien_sand, nisserne, olsen_banden):
        expected_order = [familien_sand, nisserne, olsen_banden]

        response = get_exchangescanner_response(superuser)
        tree_queryset = response.context_data['org_units']

        assert len(tree_queryset) == 3
        assert list(tree_queryset) == expected_order

    def test_exchangescanner_org_units_list_as_normal_user(
            self, user, familien_sand, nisserne, olsen_banden):
        response = get_exchangescanner_response(user)
        tree_queryset = response.context_data['org_units']
        assert len(tree_queryset) == 0

    def test_exchangescanner_generate_source_should_use_orgunit_when_both_userlist_and_orgunit_are_present(  # noqa E501: line too long
            self,
            exchange_scanner_with_userlist,
            nisserne,
            fritz,
            günther,
            hansi,
            fritz_email_alias):
        """ The used scannerjob has a filepath stored but also an org_unit chosen.
        The system should choose to use the org_unit selected."""

        exchange_scanner_with_userlist.org_unit.add(nisserne)
        exchange_scanner_with_userlist.authentication.set_password("password")
        exchange_scanner_source = exchange_scanner_with_userlist.generate_sources()

        # Goes through the generator (Only one in this case because Günther and
        # Hansi have no email alias)
        # Checks the user on the EWSAccountSource
        for ews_source in exchange_scanner_source:
            assert ews_source.user == fritz.username

    def test_exchangescanner_generate_source_with_no_email_aliases_in_org_unit(
            self,
            exchange_scanner_with_userlist,
            nisserne,
            fritz,
            günther,
            hansi):

        exchange_scanner_with_userlist.org_unit.add(nisserne)
        exchange_scanner_with_userlist.authentication.set_password("password")
        exchange_scanner_source = exchange_scanner_with_userlist.generate_sources()

        for ews_source in exchange_scanner_source:
            assert ews_source.user is None

    def test_exchangescanner_generate_source_org_unit_user_length(
            self,
            exchange_scanner_with_userlist,
            nisserne,
            fritz_email_alias,
            günther_email_alias,
            hansi_email_alias):
        """ Test that amount of sources yielded correspond to amount
        of users with email aliases"""

        sources_yielded = 0  # Store a count
        exchange_scanner_with_userlist.org_unit.add(nisserne)
        exchange_scanner_with_userlist.authentication.set_password("password")
        exchange_scanner_source = exchange_scanner_with_userlist.generate_sources()

        for _ews_source in exchange_scanner_source:
            sources_yielded += 1

        assert sources_yielded == 3

    def test_exchangescanner_generate_source_with_uploaded_userlist(
            self,
            exchange_scanner_with_userlist):
        sources_yielded = 0  # Store a count
        exchange_scanner_with_userlist.authentication.set_password("password")
        exchange_scanner_source = exchange_scanner_with_userlist.generate_sources()

        for _ews_source in exchange_scanner_source:
            sources_yielded += 1

        assert sources_yielded == 3

    def test_create_form_adds_authenthication_fields(self, user_admin):
        """Tests whether authentication is properly added in an exchangescan"""
        create_view = ExchangeScannerCreate()
        request = RequestFactory().post('/exchangescanners/add/')
        request.user = user_admin
        create_view.setup(request)

        create_form = create_view.get_form()
        assert 'username' in create_form.cleaned_data
        assert 'password' in create_form.cleaned_data

    def test_update_form_adds_authenthication_fields(self, exchange_scanner, user_admin):
        """Tests whether authentication is properly added in an exchangescan"""
        update_view = ExchangeScannerUpdate()
        request = RequestFactory().post(
            reverse('exchangescanner_update', kwargs={'pk': exchange_scanner.pk})
        )
        request.user = user_admin
        update_view.setup(request, pk=exchange_scanner.pk)

        update_form = update_view.get_form()

        assert 'username' in update_form.cleaned_data
        assert 'password' in update_form.cleaned_data

    def test_copy_form_adds_authenthication_fields(self, exchange_scanner, user_admin):
        """Tests whether authentication is properly added in an exchangescan"""
        copy_view = ExchangeScannerCopy()
        request = RequestFactory().post(
            reverse('exchangescanner_copy', kwargs={'pk': exchange_scanner.pk})
        )
        request.user = user_admin
        copy_view.setup(request, pk=exchange_scanner.pk)

        copy_form = copy_view.get_form()

        assert 'username' in copy_form.cleaned_data
        assert 'password' in copy_form.cleaned_data

    @pytest.mark.parametrize('userlist,valid', [
        (
            SimpleUploadedFile(
                'userlist_with_domains.txt',
                b'egon@olsenbanden.com\nbenny@olsenbanden.com\nkjeld@olsenbanden.com'),
            False
        ),
        (
            SimpleUploadedFile(
                'userlist_comma_separated.txt',
                b'egon,benny,kjeld'),
            False
        ),
        (
            SimpleUploadedFile(
                'userlist_whitespace_separated',
                b'egon benny kjeld'),
            False
        ),
        (
            SimpleUploadedFile('correct_userlist.txt', b'egon\nbenny\nkjeld'),
            True
        )
    ])
    def test_userlist_formatting(self, client, user_admin, test_org, basic_rule, userlist, valid):
        """Makes sure that field errors are raised when the formatting of the
        userlist is wrong. The correct formatting is username-parts of
        email-addresses separated by newlines."""

        client.force_login(user_admin)

        response = client.post(reverse('exchangescanner_add'), {
            'name': 'test_scanner',
            'mail_domain': '@test.mail',
            'organization': test_org.uuid,
            'validation_status': 0,
            'username': 'dummy',
            'password': 'super_secret',
            'userlist': userlist,
            'rule': basic_rule.pk
        })

        context = response.context
        form = context.get('form') if context else None
        # If the userlist is incorrectly formatted, the form will exist in the
        # context. If it is correctly formatted, the form will not exist.
        userlist_is_valid = form is None

        assert userlist_is_valid == valid

    @pytest.mark.parametrize('mail_domain,valid', [
        (
            'olsenbanden.com',
            False
        ),
        (
            '',
            False
        ),
        (
            '@',
            False
        ),
        (
            '@olsenbanden.com',
            True
        )
    ])
    def test_domain_formatting(
            self,
            client,
            user_admin,
            test_org,
            nisserne,
            basic_rule,
            mail_domain,
            valid):
        """Makes sure that field errors are raised when the formatting of the
        domain is wrong."""

        client.force_login(user_admin)

        response = client.post(reverse('exchangescanner_add'), {
            'name': 'test_scanner',
            'mail_domain': mail_domain,
            'organization': test_org.uuid,
            'validation_status': 0,
            'username': 'dummy',
            'password': 'super_secret',
            'org_unit': nisserne.uuid,
            'rule': basic_rule.pk
        })

        context = response.context
        form = context.get('form') if context else None
        # If the domain is incorrectly formatted, the form will exist in the
        # context. If it is correctly formatted, the form will not exist.
        domain_is_valid = form is None

        assert domain_is_valid == valid
