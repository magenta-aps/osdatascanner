import pytest
import urllib

from django.urls import reverse_lazy
from django.contrib.auth import get_user_model

from ..models import Account, Organization, Alias
from ...core.models import Client, Administrator
from ...adminapp.models.scannerjobs.webscanner import WebScanner
from ...adminapp.models.rules import CustomRule


@pytest.fixture
def olsen_banden():
    superuser = get_user_model().objects.create(username='superuser', is_superuser=True)
    regular_user = get_user_model().objects.create(username="regular_user")

    # Olsen Banden
    ob_client = Client.objects.create(name='Olsen Banden')
    olsen_banden = Organization.objects.create(name='Olsen Banden', client=ob_client)
    ob_admin = get_user_model().objects.create(username='olsen_banden_admin')
    Administrator.objects.create(user=ob_admin, client=ob_client)

    Account.objects.bulk_create([
        Account(username='manden_med_planen', first_name='Egon',
                last_name='Olsen', organization=olsen_banden),
        Account(username='ben123', first_name='Benny',
                last_name='Frandsen', organization=olsen_banden),
        Account(username='yvonneogkjeld', first_name='Kjeld',
                last_name='Jensen', organization=olsen_banden)
    ])

    egon = Account.objects.get(username='manden_med_planen')

    egon_url = reverse_lazy(
            'account',
            kwargs={
                'org_slug': olsen_banden.slug,
                'pk': egon.uuid})

    ob_url = reverse_lazy('accounts', kwargs={'org_slug': olsen_banden.slug})

    # Ninja Turtles
    nt_client = Client.objects.create(name='Teenage Mutant Ninja Turtles')
    ninja_turtles = Organization.objects.create(name="Ninja Turtles", client=nt_client)
    nt_admin = get_user_model().objects.create(username="ninja_turtles_admin")
    Administrator.objects.create(user=nt_admin, client=nt_client)

    Account.objects.bulk_create([
        Account(username="katana", first_name="Leonardo", organization=ninja_turtles),
        Account(username="sai", first_name="Raphael", organization=ninja_turtles),
        Account(username="bo", first_name="Donatello", organization=ninja_turtles),
        Account(username="nunchuck", first_name="Michelangelo", organization=ninja_turtles)
    ])

    leo = Account.objects.get(username="katana")

    leo_url = reverse_lazy(
        'account',
        kwargs={
            'org_slug': ninja_turtles.slug,
            'pk': leo.uuid})

    nt_url = reverse_lazy('accounts', kwargs={'org_slug': ninja_turtles.slug})

    # Scanners
    rule = CustomRule.objects.create(name="custom", organization=None, _rule="{}")

    # On bulk_create: ValueError: Can't bulk create a multi-table inherited model
    ob_scanner1 = WebScanner.objects.create(name="scanner1", organization=olsen_banden, rule=rule)
    ob_scanner2 = WebScanner.objects.create(name="scanner2", organization=olsen_banden, rule=rule)
    WebScanner.objects.create(name="scanner3", organization=ninja_turtles, rule=rule)

    # Aliases

    Alias.objects.bulk_create([
        Alias(imported=True, imported_id="real_id1", account=egon,
              _alias_type="email", _value="egon@olsen.dk"),
        Alias(imported=True, imported_id="real_id2", account=egon,
              _alias_type="SID", _value="SID-123"),
        Alias(imported=False, account=egon,
              _alias_type="generic", _value="olsenbanden.dk"),
        Alias(imported=False, account=egon,
              _alias_type="remediator", _value=ob_scanner2.pk),
        Alias(imported=True, imported_id="real_id3", account=leo,
              _alias_type="email", _value="leo@tmnt.dk"),
    ])

    return {
        "superuser": superuser,
        "regular_user": regular_user,
        "ob_admin": ob_admin,
        "nt_admin": nt_admin,
        "ob_url": ob_url,
        "egon_url": egon_url,
        "nt_url": nt_url,
        "leo_url": leo_url,
        "ob_scanner1": ob_scanner1,
        "ob_scanner2": ob_scanner2
    }


@pytest.mark.django_db
class TestAccountListView:

    @pytest.fixture(autouse=True)
    def setup_org(self, test_org, oluf, gertrud, benny):
        pass

    @pytest.fixture
    def url(self, test_org):
        return reverse_lazy('accounts', kwargs={'org_slug': test_org.slug})

    def test_search_query_full_name(self, superuser, url, oluf, client):
        # Arrange
        client.force_login(superuser)
        query = urllib.parse.urlencode({'search_field': 'oluf sand'})

        # Act
        response = client.get(url + '?' + query)
        accounts = response.context['accounts']

        # Assert
        assert accounts.count() == 1
        assert accounts.first() == oluf

    def test_search_query_username(self, superuser, url, oluf, client):
        # Arrange
        client.force_login(superuser)
        query = urllib.parse.urlencode({"search_field": "kartoffeloluf"})

        # Act
        response = client.get(url + '?' + query)
        accounts = response.context['accounts']

        # Assert
        assert accounts.count() == 1
        assert accounts.first() == oluf

    def test_search_query_first_name(self, superuser, url, oluf, client):
        # Arrange
        client.force_login(superuser)
        query = urllib.parse.urlencode({"search_field": "oluf"})

        # Act
        response = client.get(url + '?' + query)
        accounts = response.context['accounts']

        # Assert
        assert accounts.count() == 1
        assert accounts.first() == oluf

    def test_search_query_last_name(self, superuser, url, oluf, gertrud, client):
        # Arrange
        client.force_login(superuser)
        query = urllib.parse.urlencode({"search_field": "sand"})

        # Act
        response = client.get(url + '?' + query)
        accounts = response.context['accounts']

        # Assert
        assert accounts.count() == 2
        assert list(accounts) == [gertrud, oluf]

    def test_account_list_order(self, client, olsen_banden):
        # Arrange
        client.force_login(olsen_banden["ob_admin"])
        expected_order = ['ben123', 'manden_med_planen', 'yvonneogkjeld']

        # Act
        response = client.get(olsen_banden["ob_url"])
        accounts = response.context['accounts'].values_list('username', flat=True)

        # Assert
        assert all([username[0] == username[1] for username in zip(accounts, expected_order)])

    def test_account_list_superuser_access(self, client, olsen_banden):
        # Arrange
        client.force_login(olsen_banden["superuser"])

        # Act
        ob_response = client.get(olsen_banden["ob_url"])
        nt_response = client.get(olsen_banden["nt_url"])

        # Assert
        assert ob_response.status_code == 200
        assert nt_response.status_code == 200

    def test_account_list_admin_access(self, client, olsen_banden):
        # Arrange
        client.force_login(olsen_banden["ob_admin"])

        # Act
        ob_response = client.get(olsen_banden["ob_url"])
        nt_response = client.get(olsen_banden["nt_url"])

        # Assert
        assert ob_response.status_code == 200
        assert nt_response.status_code == 404

    def test_account_list_regular_user_access(self, client, olsen_banden):
        # Arrange
        client.force_login(olsen_banden["regular_user"])

        # Act
        ob_response = client.get(olsen_banden["ob_url"])
        nt_response = client.get(olsen_banden["nt_url"])

        # Assert
        assert ob_response.status_code == 404
        assert nt_response.status_code == 404

    def test_account_list_logged_out_access(self, client, olsen_banden):
        # Arrange
        client.logout()

        # Act
        ob_response = client.get(olsen_banden["ob_url"])
        nt_response = client.get(olsen_banden["nt_url"])

        # Assert
        assert ob_response.status_code == 302
        assert nt_response.status_code == 302


@pytest.mark.django_db
class TestAccountDetailView:

    def test_account_detail_superuser_get_access(self, client, olsen_banden):
        # Arrange
        client.force_login(olsen_banden["superuser"])

        # Act
        egon_response = client.get(olsen_banden["egon_url"])
        leo_response = client.get(olsen_banden["leo_url"])

        # Assert
        assert egon_response.status_code == 200
        assert leo_response.status_code == 200

    def test_account_detail_admin_get_access(self, client, olsen_banden):
        # Arrange
        client.force_login(olsen_banden["ob_admin"])

        # Act
        egon_response = client.get(olsen_banden["egon_url"])
        leo_response = client.get(olsen_banden["leo_url"])

        # Assert
        assert egon_response.status_code == 200
        assert leo_response.status_code == 404

    def test_account_detail_regular_user_get_access(self, client, olsen_banden):
        # Arrange
        client.force_login(olsen_banden["regular_user"])

        # Act
        egon_response = client.get(olsen_banden["egon_url"])
        leo_response = client.get(olsen_banden["leo_url"])

        # Assert
        assert egon_response.status_code == 404
        assert leo_response.status_code == 404

    def test_account_detail_logged_out_get_access(self, client, olsen_banden):
        # Arrange
        client.logout()

        # Act
        egon_response = client.get(olsen_banden["egon_url"])
        leo_response = client.get(olsen_banden["leo_url"])

        # Assert
        assert egon_response.status_code == 302
        assert leo_response.status_code == 302

    def test_account_detail_superuser_post_access(self, client, olsen_banden):
        # Arrange
        client.force_login(olsen_banden["superuser"])

        # Act
        egon_response = client.post(olsen_banden["egon_url"])
        leo_response = client.post(olsen_banden["leo_url"])

        # Assert
        assert egon_response.status_code == 200
        assert leo_response.status_code == 200

    def test_account_detail_admin_post_access(self, client, olsen_banden):
        # Arrange
        client.force_login(olsen_banden["ob_admin"])

        # Act
        egon_response = client.post(olsen_banden["egon_url"])
        leo_response = client.post(olsen_banden["leo_url"])

        # Assert
        assert egon_response.status_code == 200
        assert leo_response.status_code == 404

    def test_account_detail_regular_user_post_access(self, client, olsen_banden):
        # Arrange
        client.force_login(olsen_banden["regular_user"])

        # Act
        egon_response = client.post(olsen_banden["egon_url"])
        leo_response = client.post(olsen_banden["leo_url"])

        # Assert
        assert egon_response.status_code == 404
        assert leo_response.status_code == 404

    def test_account_detail_logged_out_post_access(self, client, olsen_banden):
        # Arrange
        client.logout()

        # Act
        egon_response = client.post(olsen_banden["egon_url"])
        leo_response = client.post(olsen_banden["leo_url"])

        # Assert
        assert egon_response.status_code == 302
        assert leo_response.status_code == 302

    def test_account_detail_aliases(self, client, olsen_banden):
        # Arrange
        client.force_login(olsen_banden["ob_admin"])

        # Act
        response = client.get(olsen_banden["egon_url"])
        imported_aliases = response.context['imported_aliases']
        other_aliases = response.context['other_aliases']

        # Assert
        assert imported_aliases.count() == 2
        assert other_aliases.count() == 1

    def test_account_detail_remediator_for_scanners(self, client, olsen_banden):
        # Arrange
        client.force_login(olsen_banden["ob_admin"])

        # Act
        response = client.get(olsen_banden["egon_url"])
        rem_scanners = response.context['remediator_for_scanners']

        # Assert
        assert len(rem_scanners) == 1

    @pytest.mark.parametrize("user,response_code,count", [
        ("ob_admin", 200, 1),
        ("superuser", 200, 1),
        ("nt_admin", 404, 0),
        ("regular_user", 404, 0)])
    def test_account_detail_remediator_check(
            self, client, olsen_banden, user, response_code, count):
        # Arrange
        client.force_login(olsen_banden[user])

        # Act
        response = client.post(
            olsen_banden["egon_url"],
            data={"remediator-check": "on"},
            **{"HTTP_HX-Trigger-Name": "remediator-check"}
            )

        # Assert
        assert response.status_code == response_code
        assert Alias.objects.filter(
            account=Account.objects.get(
                username="manden_med_planen"),
            _alias_type="remediator",
            _value=0).count() == count

    @pytest.mark.parametrize("user,response_code,count", [
        ("ob_admin", 200, 1),
        ("superuser", 200, 1),
        ("nt_admin", 404, 0),
        ("regular_user", 404, 0)])
    def test_account_detail_admin_add_remediator(
            self, client, olsen_banden, user, response_code, count):
        # Arrange
        client.force_login(olsen_banden[user])
        ob_scanner1 = olsen_banden["ob_scanner1"]

        # Act
        response = client.post(
            olsen_banden["egon_url"],
            data={"add-remediator": ob_scanner1.pk},
            **{"HTTP_HX-Trigger-Name": "add-remediator"}
            )

        # Assert
        assert response.status_code == response_code
        assert Alias.objects.filter(
            account=Account.objects.get(
                username="manden_med_planen"),
            _alias_type="remediator",
            _value=ob_scanner1.pk).count() == count

    @pytest.mark.parametrize("user,response_code,count", [
        ("ob_admin", 200, 0),
        ("superuser", 200, 0),
        ("nt_admin", 404, 1),
        ("regular_user", 404, 1)])
    def test_account_detail_admin_rem_remediator(
            self, client, olsen_banden, user, response_code, count):
        # Arrange
        client.force_login(olsen_banden[user])
        ob_scanner2 = olsen_banden["ob_scanner2"]

        # Act
        response = client.post(
            olsen_banden["egon_url"],
            data={"rem-remediator": ob_scanner2.pk},
            **{"HTTP_HX-Trigger-Name": "rem-remediator"}
        )

        # Assert
        assert response.status_code == response_code
        assert Alias.objects.filter(
            account=Account.objects.get(username="manden_med_planen"),
            _alias_type="remediator",
            _value=ob_scanner2.pk).count() == count
