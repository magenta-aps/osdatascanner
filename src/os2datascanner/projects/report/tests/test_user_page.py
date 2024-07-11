import pytest
from django.test import override_settings
from django.urls.base import reverse
from django.contrib.auth.models import AnonymousUser

from ..reportapp.views.user_views import AccountView


@pytest.mark.django_db
class TestAccountView:

    def test_user_page_as_roleless_user(self, egon_account, rf):
        """A user without a role should be able to see the page."""
        view = self.get_userpage_object(rf, egon_account)

        assert view.status_code == 200

    def test_user_page_as_roleless_superuser(self, rf, superuser_account):
        """A superuser without a role should be able to see the page."""

        view = self.get_userpage_object(rf, superuser_account)

        assert view.status_code == 200

    @override_settings(LANGUAGE_CODE='en-US', LANGUAGES=(('en', 'English'),))
    def test_user_page_as_dpo_user(self, rf, egon_account, egon_dpo_position):
        """A DPO should be able to see the page, and the DPO-role should be
        displayed."""
        view = self.get_userpage_object(rf, egon_account)

        assert view.status_code == 200

    def test_anonymous_user_redirect(self, rf):
        """A user who is not logged in should be redirected."""
        request = rf.get('/account')
        request.user = AnonymousUser()
        response = AccountView.as_view()(request)
        assert response.status_code == 302

    def test_user_aliases_are_sent_to_user_view_context(
            self, rf, egon_account, egon_email_alias, egon_sid_alias):
        """The aliases connected to an account should be displayed on that
        account's page."""

        view = self.get_userpage_object(rf, egon_account)

        assert egon_email_alias._value in str(view.context_data['aliases'])
        assert egon_sid_alias._value in str(view.context_data['aliases'])

    @override_settings(LANGUAGE_CODE='en-US', LANGUAGES=(('en', 'English'),))
    def test_superuser_can_see_is_superuser_checkmark(self, rf, superuser_account):
        """A superuser should be able to see their superuser checkmark."""
        view = self.get_userpage_object(rf, superuser_account)

        assert '<td>Superuser</td>' in view.rendered_content

    @override_settings(LANGUAGE_CODE='en-US', LANGUAGES=(('en', 'English'),))
    def test_non_superuser_can_not_see_is_superuser_checkmark(self, rf, egon_account):
        """A user, who is not a superuser, should not see a superuser
        checkmark."""
        view = self.get_userpage_object(rf, egon_account)
        assert '<td>Superuser</td>' not in view.rendered_content

    @override_settings(LANGUAGE_CODE='en-US', LANGUAGES=(('en', 'English'),))
    def test_user_can_see_link_to_password_change(self, egon_account, rf):
        """Users should be able to see a link to password change."""
        view = self.get_userpage_object(rf, egon_account)
        url = '<a class="password-change" href="%s">Change</a>' % reverse('password_change')
        assert url in view.rendered_content

    def test_access_other_user_account(self, client, egon_account, benny_account):
        """An unprivileged user should not be able to access the page of
        another account."""
        client.force_login(egon_account.user)
        response = client.get(reverse('account', kwargs={'pk': benny_account.pk}))

        assert response.status_code == 403

    def test_access_other_user_account_as_superuser(self, client, superuser_account, egon_account):
        """A superuser should be able to access the page of another account."""
        client.force_login(superuser_account.user)
        response = client.get(reverse('account', kwargs={'pk': egon_account.pk}))

        assert response.status_code == 200
        assert response.context_data['account'] == egon_account

    # Helper functions

    def get_userpage_object(self, rf, account):
        request = rf.get('/account')
        request.user = account.user
        response = AccountView.as_view()(request)
        return response
