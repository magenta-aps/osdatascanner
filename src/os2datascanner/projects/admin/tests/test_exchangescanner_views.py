from parameterized import parameterized

from django.test import TestCase, RequestFactory
from django.urls.base import reverse
from django.utils.text import slugify
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile

from ..adminapp.models.rules import Rule
from ..adminapp.models.authentication import Authentication
from ..adminapp.models.scannerjobs.exchangescanner import ExchangeScanner
from ..adminapp.views.exchangescanner_views import (
    ExchangeScannerCopy, ExchangeScannerCreate, ExchangeScannerUpdate)
from ..core.models import Administrator
from ..core.models.client import Client
from ..organizations.models import OrganizationalUnit, Account, Alias
from ..organizations.models.aliases import AliasType
from ..organizations.models.organization import Organization


class ExchangeScannerViewsTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        client1 = Client.objects.create(
            name="client1",
        )

        magenta_org = Organization.objects.create(
            name="Magenta ApS",
            uuid="5d02dfd3-b31c-4076-b2d5-4e41d3442952",
            slug=slugify("Magenta ApS"),
            client=client1,
        )

        magenta_org_unit0 = OrganizationalUnit.objects.create(
            name="Magenta Org. Unit",
            uuid="c0f966ea-af0f-4e81-bd65-b0967a47c3a7",
            organization=magenta_org,
        )

        magenta_org_unit1 = OrganizationalUnit.objects.create(
            name="Magenta Org. Unit1",
            uuid="20e842fc-2671-4e85-8217-454cb01b18ec",
            parent=magenta_org_unit0,
            organization=magenta_org,
        )

        OrganizationalUnit.objects.create(
            name="Magenta Org. Unit2",
            uuid="b50e34c2-4e61-4cae-b08d-19fac55d3e35",
            parent=magenta_org_unit1,
            organization=magenta_org,
        )

        client2 = Client.objects.create(name="client2")
        test_org = Organization.objects.create(
            name="Test",
            uuid="bddb5188-1240-4733-8700-b57ba6228850",
            slug=slugify("Test"),
            client=client2,
        )

        test_org_unit0 = OrganizationalUnit.objects.create(
            name="Test Org. Unit",
            uuid="466c3f4e-3f64-4c9b-b6ae-26726721a28f",
            organization=test_org,
        )

        test_org_unit1 = OrganizationalUnit.objects.create(
            name="Test Org. Unit1",
            uuid="d063b582-fcd5-4a36-a99a-7785321de083",
            parent=test_org_unit0,
            organization=test_org,
        )

        OrganizationalUnit.objects.create(
            name="Test Org. Unit2",
            uuid="4cae2e75-fd10-428e-aa53-6f077da53d51",
            organization=test_org,
        )

        benny_account = Account.objects.create(
            uuid="1cae2e34-fd56-428e-aa53-6f077da53d51",
            username="BeOls",
            first_name="Benny",
            last_name="Olsen",
            organization=magenta_org,
        )

        yvonne_account = Account.objects.create(
            uuid="1cae2e37-fd99-428e-aa53-6f077da53d51",
            username="YvJen",
            first_name="Yvonne",
            last_name="Jensen",
            organization=magenta_org,
        )

        Alias.objects.create(
            uuid="1cae2e34-fd56-428e-aa53-6f077da12d99",
            account=benny_account,
            alias_type=AliasType.EMAIL,
            value='Benny@Olsen.dk',
        )

        scanner_auth_obj = Authentication.objects.create(
            username="ImExchangeAdmin",
            domain="ThisIsMyExchangeDomain",
        )

        exchange_rule = Rule.objects.create(
            organization=magenta_org,
            name="cool rule",
        )

        exchange_scan = ExchangeScanner.objects.create(
            pk=100,
            name="This is an Exchange Scanner",
            organization=magenta_org,
            validation_status=ExchangeScanner.VALID,
            userlist=SimpleUploadedFile("dummy.txt", b"aleph\nalex\nfred"),
            service_endpoint="exchangeendpoint",
            authentication=scanner_auth_obj,
        )
        exchange_scan.rules.set([exchange_rule])
        exchange_scan.org_unit.set([test_org_unit0, test_org_unit1])

        def generate_file():
            try:
                myfile = open('user_list.txt', 'w')
                myfile.write('user1\n')
                myfile.write('user2\n')
                myfile.write('user3\n')
            finally:
                myfile.close()

            return myfile

        scanner_auth_obj_2 = Authentication.objects.create(
            username="ImExchangeAdmin",
            domain="ThisIsMyExchangeDomain",
        )

        ExchangeScanner.objects.create(
            pk=200,
            name="This is an Exchange Scanner with userlist",
            organization=magenta_org,
            validation_status=ExchangeScanner.VALID,
            service_endpoint="exchangeendpoint",
            authentication=scanner_auth_obj_2,
        )

        benny_account.units.add(test_org_unit1)
        yvonne_account.units.add(test_org_unit0)

    def setUp(self):
        self.factory = RequestFactory()
        self.kjeld = get_user_model().objects.create_user(
            username='kjeld', email='kjeld@jensen.com', password='top_secret')
        # Egon is admin
        self.egon = get_user_model().objects.create_user(
            username='egon', email='egon@olsen.com', password='no_secret')
        Administrator.objects.create(user=self.egon, client=Client.objects.get(name="client1"))

        self.benny_alias = Alias.objects.get(uuid="1cae2e34-fd56-428e-aa53-6f077da12d99")
        self.yvonne = Account.objects.get(uuid="1cae2e37-fd99-428e-aa53-6f077da53d51")
        self.exchange_scan = ExchangeScanner.objects.get(pk=100)

    def test_exchangesscanner_org_units_list_as_administrator(self):
        """Note that this is not a django administrator role,
        but instead an organization administrator.
        Egon has this role."""
        request = self.factory.get('/exchangescanners/add/')
        request.user = self.egon
        response = ExchangeScannerCreate.as_view()(request)

        tree_queryset = response.context_data['org_units']
        self.assertEqual(len(tree_queryset), 3)
        self.assertEqual(str(tree_queryset[0].uuid),
                         "c0f966ea-af0f-4e81-bd65-b0967a47c3a7")
        self.assertEqual(str(tree_queryset[1].uuid),
                         "20e842fc-2671-4e85-8217-454cb01b18ec")
        self.assertEqual(str(tree_queryset[2].uuid),
                         "b50e34c2-4e61-4cae-b08d-19fac55d3e35")
        self.assertEqual(str(tree_queryset[2].parent.uuid),
                         str(tree_queryset[1].uuid))

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

    def test_exchangescanner_org_units_list_as_superuser(self):
        self.kjeld.is_superuser = True
        response = self.get_exchangescanner_response()
        tree_queryset = response.context_data['org_units']
        self.assertEqual(len(tree_queryset), 6)
        self.assertEqual(str(tree_queryset[3].uuid),
                         "466c3f4e-3f64-4c9b-b6ae-26726721a28f")
        self.assertEqual(str(tree_queryset[4].parent.uuid),
                         str(tree_queryset[3].uuid))
        self.kjeld.is_superuser = False

    def test_exchangescanner_org_units_list_as_normal_user(self):
        response = self.get_exchangescanner_response()
        tree_queryset = response.context_data['org_units']
        self.assertEqual(len(tree_queryset), 0)

    def test_exchangescanner_generate_source_should_use_orgunit_when_both_userlist_and_orgunit_are_present(self):  # noqa
        """ The used scannerjob has a filepath stored but also an org_unit chosen.
        The system should choose to use the org_unit selected.

        Only Benny has an email alias and will have an
        EWSAccountSource object yielded"""

        exchange_scanner_obj = ExchangeScanner.objects.get(pk=100)
        exchange_scanner_obj.authentication.set_password("password")
        exchange_scanner_source = exchange_scanner_obj.generate_sources()

        # Goes through the generator (Only one in this case because Yvonne has no email alias)
        # Checks the user on the EWSAccountSource
        for ews_source in exchange_scanner_source:
            self.assertEqual(ews_source.user, "Benny")

    def test_exchangescanner_generate_source_with_no_email_aliases_in_org_unit(self):

        exchange_scanner_obj = ExchangeScanner.objects.get(pk=100)
        exchange_scanner_obj.authentication.set_password("password")

        # Delete Benny's alias in this case.
        self.benny_alias.delete()

        exchange_scanner_source = exchange_scanner_obj.generate_sources()
        for ews_source in exchange_scanner_source:
            self.assertEqual(ews_source.user, None)

    def test_exchangescanner_generate_source_org_unit_user_length(self):
        """ Test that amount of sources yielded correspond to amount
        of users with email aliases"""
        sources_yielded = 0  # Store a count
        exchange_scanner_obj = ExchangeScanner.objects.get(pk=100)
        exchange_scanner_obj.authentication.set_password("password")

        # Give Yvonne an email alias.
        yvonne_alias = Alias.objects.create(
            uuid="1bae4e34-fd56-428e-aa53-6f077da12d99",
            account=self.yvonne,
            alias_type=AliasType.EMAIL,
            value='Yvonne@Jensen.dk',
        )

        exchange_scanner_source = exchange_scanner_obj.generate_sources()
        for _ews_source in exchange_scanner_source:
            sources_yielded += 1

        # benny is a member of test_org_unit1
        # yvonne is a member of test_org_unit0
        self.assertEqual(sources_yielded, 2)

        yvonne_alias.delete()

    def test_exchangescanner_generate_source_with_uploaded_userlist(self):
        sources_yielded = 0  # Store a count
        exchange_scanner_obj = ExchangeScanner.objects.get(pk=200)
        exchange_scanner_obj.authentication.set_password("password")

        exchange_scanner_obj.userlist = SimpleUploadedFile("dummy.txt",
                                                           b"aleph\nalex\nfred")

        exchange_scanner_source = exchange_scanner_obj.generate_sources()
        for _ews_source in exchange_scanner_source:
            sources_yielded += 1

        self.assertEqual(sources_yielded, 3)

    def get_exchangescanner_response(self):
        request = self.factory.get('/exchangescanners/add/')
        request.user = self.kjeld
        response = ExchangeScannerCreate.as_view()(request)
        return response

    def test_create_form_adds_authenthication_fields(self):
        """Tests whether authentication is properly added in an exchangescan"""
        create_view = ExchangeScannerCreate()
        request = self.factory.post('/exchangescanners/add/')
        request.user = self.kjeld
        create_view.setup(request)

        create_form = create_view.get_form()
        self.assertTrue('username' in create_form.cleaned_data)
        self.assertTrue('password' in create_form.cleaned_data)

    def test_update_form_adds_authenthication_fields(self):
        """Tests whether authentication is properly added in an exchangescan"""
        update_view = ExchangeScannerUpdate()
        request = self.factory.post(
            reverse('exchangescanner_update', kwargs={'pk': self.exchange_scan.pk})
        )
        request.user = self.egon
        update_view.setup(request, pk=self.exchange_scan.pk)

        update_form = update_view.get_form()
        self.assertTrue('username' in update_form.cleaned_data)
        self.assertTrue('password' in update_form.cleaned_data)

    def test_copy_form_adds_authenthication_fields(self):
        """Tests whether authentication is properly added in an exchangescan"""
        copy_view = ExchangeScannerCopy()
        request = self.factory.post(
            reverse('exchangescanner_copy', kwargs={'pk': self.exchange_scan.pk})
        )
        request.user = self.kjeld
        copy_view.setup(request, pk=self.exchange_scan.pk)

        copy_form = copy_view.get_form()
        self.assertTrue('username' in copy_form.cleaned_data)
        self.assertTrue('password' in copy_form.cleaned_data)

    @parameterized.expand([
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
    def test_userlist_formatting(self, userlist, valid):
        """Makes sure that field errors are raised when the formatting of the
        userlist is wrong. The correct formatting is username-parts of
        email-addresses separated by newlines."""

        self.client.force_login(self.egon)

        response = self.client.post(reverse('exchangescanner_add'), {
            'name': 'test_scanner',
            'mail_domain': '@test.mail',
            'organization': '5d02dfd3-b31c-4076-b2d5-4e41d3442952',
            'validation_status': 0,
            'username': 'dummy',
            'password': 'super_secret',
            'userlist': userlist,
            'rules': 1
        })

        context = response.context
        form = context.get('form') if context else None
        # If the userlist is incorrectly formatted, the form will exist in the
        # context. If it is correctly formatted, the form will not exist.
        userlist_is_valid = form is None

        self.assertEqual(userlist_is_valid, valid)
