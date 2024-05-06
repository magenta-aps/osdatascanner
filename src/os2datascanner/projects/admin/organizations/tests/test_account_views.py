import pytest
import urllib

from django.urls import reverse_lazy

from os2datascanner.projects.admin.organizations.models import Alias


@pytest.mark.django_db
class TestAccountListView:

    @pytest.fixture(autouse=True)
    def setup_org(self, test_org, oluf, gertrud, benny):
        pass

    @pytest.fixture
    def url(self, test_org):
        return reverse_lazy('accounts', kwargs={'org_slug': test_org.slug})

    @pytest.fixture
    def other_url(self, test_org2):
        return reverse_lazy('accounts', kwargs={'org_slug': test_org2.slug})

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

    def test_account_list_order(self, user_admin, url, nisserne_accounts, client):
        # Arrange
        client.force_login(user_admin)
        expected_order = nisserne_accounts.order_by(
            'first_name', 'last_name').values_list(
            'username', flat=True)

        # Act
        response = client.get(url)
        usernames = response.context['accounts'].values_list('username', flat=True)

        # Assert
        assert all([username[0] == username[1] for username in zip(usernames, expected_order)])

    @pytest.mark.parametrize("access_user,expected_codes", [
        ("superuser", [200, 200]),
        ("admin", [200, 404]),
        ("regular_user", [404, 404]),
        ("anonymous", [302, 302]),
    ])
    def test_account_list_access(
            self,
            access_user,
            expected_codes,
            superuser,
            user_admin,
            user,
            url,
            other_url,
            nisserne,
            client):
        # Arrange
        users = {"superuser": superuser, "admin": user_admin, "regular_user": user}
        if access_user == "anonymous":
            client.logout()
        else:
            client.force_login(users[access_user])

        # Act
        response1 = client.get(url)
        response2 = client.get(other_url)

        # Assert
        assert response1.status_code == expected_codes[0]
        assert response2.status_code == expected_codes[1]


@pytest.mark.django_db
class TestAccountDetailView:

    @pytest.fixture
    def fritz_url(self, test_org, fritz):
        return reverse_lazy('account', kwargs={'org_slug': test_org.slug, 'pk': fritz.uuid})

    @pytest.fixture
    def egon_url(self, test_org2, egon):
        return reverse_lazy('account', kwargs={'org_slug': test_org2.slug, 'pk': egon.uuid})

    @pytest.mark.parametrize("access_user,method,expected_codes", [
        ("superuser", "GET", [200, 200]),
        ("admin", "GET", [200, 404]),
        ("regular_user", "GET", [404, 404]),
        ("anonymous", "GET", [302, 302]),
        ("superuser", "POST", [200, 200]),
        ("admin", "POST", [200, 404]),
        ("regular_user", "POST", [404, 404]),
        ("anonymous", "POST", [302, 302]),
    ])
    def test_account_detail_access(
            self,
            access_user,
            method,
            expected_codes,
            superuser,
            user_admin,
            user,
            fritz_url,
            egon_url,
            client):
        # Arrange
        users = {"superuser": superuser, "admin": user_admin, "regular_user": user}
        if access_user == "anonymous":
            client.logout()
        else:
            client.force_login(users[access_user])

        # Act
        if method == "GET":
            response1 = client.get(fritz_url)
            response2 = client.get(egon_url)
        elif method == "POST":
            response1 = client.post(fritz_url)
            response2 = client.post(egon_url)

        # Assert
        assert response1.status_code == expected_codes[0]
        assert response2.status_code == expected_codes[1]

    def test_account_detail_aliases(
            self,
            user_admin,
            fritz_url,
            fritz_email_alias,
            fritz_shared_email_alias,
            fritz_generic_alias,
            client):
        # Arrange
        client.force_login(user_admin)
        expected_imported_aliases = [fritz_email_alias]
        expected_other_alias = [fritz_shared_email_alias, fritz_generic_alias]

        # Act
        response = client.get(fritz_url)
        imported_aliases = response.context['imported_aliases']
        other_aliases = response.context['other_aliases']

        # Assert
        assert all(alias in imported_aliases for alias in expected_imported_aliases)
        assert all(alias in other_aliases for alias in expected_other_alias)

    def test_account_detail_remediator_for_scanners(
            self, user_admin, fritz_url, fritz_remediator_alias, client):
        # Arrange
        client.force_login(user_admin)

        # Act
        response = client.get(fritz_url)
        rem_scanners = response.context['remediator_for_scanners']

        # Assert
        assert len(rem_scanners) == 1
        assert rem_scanners[0]["pk"] == fritz_remediator_alias._value

    @pytest.mark.parametrize("access_user,expected_code,expected_aliases", [
        ("admin", 200, 1),
        ("superuser", 200, 1),
        ("other_admin", 404, 0),
        ("regular_user", 404, 0),
        ("anonymous", 302, 0)])
    def test_account_detail_remediator_check(
            self,
            access_user,
            expected_code,
            expected_aliases,
            superuser,
            user_admin,
            user,
            other_admin,
            fritz_url,
            fritz,
            client):
        # Arrange
        users = {
            "superuser": superuser,
            "admin": user_admin,
            "regular_user": user,
            "other_admin": other_admin}
        if access_user == "anonymous":
            client.logout()
        else:
            client.force_login(users[access_user])

        # Act
        response = client.post(
            fritz_url,
            data={"remediator-check": "on"},
            **{"HTTP_HX-Trigger-Name": "remediator-check"}
            )

        # Assert
        assert response.status_code == expected_code
        assert Alias.objects.filter(
            account=fritz,
            _alias_type="remediator",
            _value=0).count() == expected_aliases

    @pytest.mark.parametrize("access_user,expected_code,expected_aliases", [
        ("admin", 200, 1),
        ("superuser", 200, 1),
        ("other_admin", 404, 0),
        ("regular_user", 404, 0),
        ("anonymous", 302, 0)])
    def test_account_detail_admin_add_remediator(
            self,
            access_user,
            expected_code,
            expected_aliases,
            superuser,
            user_admin,
            user,
            other_admin,
            fritz_url,
            fritz,
            basic_scanner,
            client):
        # Arrange
        users = {
            "superuser": superuser,
            "admin": user_admin,
            "regular_user": user,
            "other_admin": other_admin}
        if access_user == "anonymous":
            client.logout()
        else:
            client.force_login(users[access_user])

        # Act
        response = client.post(
            fritz_url,
            data={"add-remediator": basic_scanner.pk},
            **{"HTTP_HX-Trigger-Name": "add-remediator"}
            )

        # Assert
        assert response.status_code == expected_code
        assert Alias.objects.filter(
            account=fritz,
            _alias_type="remediator",
            _value=basic_scanner.pk).count() == expected_aliases

    @pytest.mark.parametrize("access_user,expected_code,expected_aliases", [
        ("admin", 200, 0),
        ("superuser", 200, 0),
        ("other_admin", 404, 1),
        ("regular_user", 404, 1),
        ("anonymous", 302, 1)])
    def test_account_detail_admin_rem_remediator(
            self,
            access_user,
            expected_code,
            expected_aliases,
            superuser,
            user_admin,
            user,
            other_admin,
            fritz_url,
            fritz,
            fritz_remediator_alias,
            basic_scanner,
            client):
        # Arrange
        users = {
            "superuser": superuser,
            "admin": user_admin,
            "regular_user": user,
            "other_admin": other_admin}
        if access_user == "anonymous":
            client.logout()
        else:
            client.force_login(users[access_user])

        # Act
        response = client.post(
            fritz_url,
            data={"rem-remediator": basic_scanner.pk},
            **{"HTTP_HX-Trigger-Name": "rem-remediator"}
        )

        # Assert
        assert response.status_code == expected_code
        assert Alias.objects.filter(
            account=fritz,
            _alias_type="remediator",
            _value=basic_scanner.pk).count() == expected_aliases
