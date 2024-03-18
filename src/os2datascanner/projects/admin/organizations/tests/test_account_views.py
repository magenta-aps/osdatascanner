import pytest
import urllib

from django.urls import reverse_lazy
from django.contrib.auth import get_user_model

from ..models import Account, Organization
from ...core.models import Client


@pytest.mark.django_db
class TestAccountViews:

    @classmethod
    def setup_method(cls):
        cls.superuser = get_user_model().objects.create(username='superuser', is_superuser=True)
        client = Client.objects.create(name='Olsen Banden')
        olsen_banden = Organization.objects.create(name='Olsen Banden', client=client)

        Account.objects.bulk_create([
            Account(username='manden_med_planen', first_name='Egon',
                    last_name='Olsen', organization=olsen_banden),
            Account(username='ben123', first_name='Benny',
                    last_name='Frandsen', organization=olsen_banden),
            Account(username='yvonneogkjeld', first_name='Kjeld',
                    last_name='Jensen', organization=olsen_banden)
        ])

        cls.url = reverse_lazy('accounts', kwargs={'org_slug': olsen_banden.slug})

    def test_search_query_full_name(self, client):
        # Arrange
        client.force_login(self.superuser)
        query = urllib.parse.urlencode({'search_field': 'egon olsen'})

        # Act
        response = client.get(self.url + '?' + query)
        accounts = response.context['accounts']

        # Assert
        assert accounts.count() == 1
        assert accounts.first() == Account.objects.get(username='manden_med_planen')

    def test_search_query_username(self, client):
        # Arrange
        client.force_login(self.superuser)
        query = urllib.parse.urlencode({"search_field": "ben123"})

        # Act
        response = client.get(self.url + '?' + query)
        accounts = response.context['accounts']

        # Assert
        assert accounts.count() == 1
        assert accounts.first() == Account.objects.get(username="ben123")

    def test_search_query_first_name(self, client):
        # Arrange
        client.force_login(self.superuser)
        query = urllib.parse.urlencode({"search_field": "benny"})

        # Act
        response = client.get(self.url + '?' + query)
        accounts = response.context['accounts']

        # Assert
        assert accounts.count() == 1
        assert accounts.first() == Account.objects.get(username="ben123")

    def test_search_query_last_name(self, client):
        # Arrange
        client.force_login(self.superuser)
        query = urllib.parse.urlencode({"search_field": "frandsen"})

        # Act
        response = client.get(self.url + '?' + query)
        accounts = response.context['accounts']

        # Assert
        assert accounts.count() == 1
        assert accounts.first() == Account.objects.get(username="ben123")

    # TODO: Add more tests for the account views (#60171).
