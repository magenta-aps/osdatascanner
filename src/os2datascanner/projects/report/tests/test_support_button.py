import pytest

from django.urls import reverse_lazy


@pytest.fixture
def support_button_url():
    return reverse_lazy('support_button')


@pytest.mark.django_db
class TestSupportButton:

    def test_support_button_view_configuration_true(
            self,
            client,
            egon_account,
            olsenbanden_organization,
            support_button_url):
        """Users should be able to access the SupportButtonView, as long as
        their organization has toggled the functionality on."""

        olsenbanden_organization.show_support_button = True
        olsenbanden_organization.save()

        client.force_login(egon_account.user)

        response = client.get(support_button_url)

        assert response.status_code == 200

    def test_support_button_view_configuration_false(
            self,
            client,
            egon_account,
            olsenbanden_organization,
            support_button_url):
        """If the user's organization has toggled the functionality off, the
        user should be denied access."""

        olsenbanden_organization.show_support_button = False
        olsenbanden_organization.save()

        client.force_login(egon_account.user)

        response = client.get(support_button_url)

        assert response.status_code == 404
