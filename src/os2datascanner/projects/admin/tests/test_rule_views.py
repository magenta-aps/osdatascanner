import pytest

from django.contrib.auth.models import AnonymousUser
from django.urls import reverse_lazy

from ..adminapp.models.rules import CustomRule


@pytest.fixture
def rule_data(test_org):
    return {
            "name": "dummy rule",
            "description": "this is a dumb dumb dummy rule",
            "sensitivity": 3,
            "rule": '{"type": "regex", "expression": "dummy"}',
            "organization": test_org.uuid
        }


@pytest.mark.django_db
class TestCustomRuleCreate:

    @pytest.mark.parametrize('user_fixture,method,response_code', [
        ('superuser', 'GET', 200),
        ('user_admin', 'GET', 200),
        ('user', 'GET', 200),
        ('other_admin', 'GET', 200),
        ('anonymous_user', 'GET', 302),
        ('superuser', 'POST', 302),
        ('user_admin', 'POST', 302),
        ('user', 'POST', 200),
        ('other_admin', 'POST', 200),
        ('anonymous_user', 'POST', 302),
    ])
    def test_rule_create_access(
            self,
            request,
            method,
            client,
            user_fixture,
            response_code,
            rule_data):
        """For POST-requests, response code 200 indicates that the form contains
        some errors. A correctly created rule will return a 302 redirect."""

        user = request.getfixturevalue(user_fixture)

        if method == 'GET':
            response = self.get_rule_create(client, user)
        elif method == 'POST':
            response = self.post_rule_create(client, user, rule_data)

        assert response.status_code == response_code

    def test_create_rule_form(self, client, request, user_admin, test_org, rule_data):

        self.post_rule_create(client, user_admin, rule_data)

        created_rule = CustomRule.objects.last()

        assert created_rule.name == rule_data['name']
        assert created_rule.description == rule_data['description']
        assert created_rule.sensitivity == rule_data['sensitivity']
        assert str(created_rule.organization.uuid) == rule_data['organization']

    def get_rule_create(self, client, user, **kwargs):
        if not isinstance(user, AnonymousUser):
            client.force_login(user)
        response = client.get(reverse_lazy('customrule_add'))
        return response

    def post_rule_create(self, client, user, data: dict, **kwargs):
        if not isinstance(user, AnonymousUser):
            client.force_login(user)
        response = client.post(
            reverse_lazy('customrule_add'), data, headers={
                "Content-Type": "application/json"})
        return response


@pytest.mark.django_db
class TestCustomRuleUpdate:

    @pytest.mark.parametrize('user_fixture,method,response_code', [
        ('superuser', 'GET', 200),
        ('user_admin', 'GET', 200),
        ('user', 'GET', 404),
        ('other_admin', 'GET', 404),
        ('anonymous_user', 'GET', 302),
        ('superuser', 'POST', 302),
        ('user_admin', 'POST', 302),
        ('user', 'POST', 404),
        ('other_admin', 'POST', 404),
        ('anonymous_user', 'POST', 302),
    ])
    def test_rule_update_access(
            self,
            request,
            method,
            client,
            user_fixture,
            response_code,
            rule_data,
            org_rule):
        """For POST-requests, response code 200 indicates that the form contains
        some errors. A correctly updated rule will return a 302 redirect."""

        user = request.getfixturevalue(user_fixture)

        if method == 'GET':
            response = self.get_rule_update(client, user, org_rule.pk)
        elif method == 'POST':
            response = self.post_rule_update(client, user, org_rule.pk, rule_data)

        assert response.status_code == response_code

    def test_update_rule_form(self, client, user_admin, test_org, rule_data, org_rule):

        self.post_rule_update(client, user_admin, org_rule.pk, rule_data)

        updated_rule = CustomRule.objects.get(pk=org_rule.pk)

        assert updated_rule.name == rule_data['name']
        assert updated_rule.description == rule_data['description']
        assert updated_rule.sensitivity == rule_data['sensitivity']
        assert str(updated_rule.organization.uuid) == rule_data['organization']

    def get_rule_update(self, client, user, pk, **kwargs):
        if not isinstance(user, AnonymousUser):
            client.force_login(user)
        response = client.get(reverse_lazy('customrule_update', kwargs={'pk': pk}))
        return response

    def post_rule_update(self, client, user, pk, data: dict, **kwargs):
        if not isinstance(user, AnonymousUser):
            client.force_login(user)
        response = client.post(
            reverse_lazy('customrule_update', kwargs={'pk': pk}), data, headers={
                "Content-Type": "application/json"})
        return response


@pytest.mark.django_db
class TestCustomRuleDelete:

    @pytest.mark.parametrize('user_fixture,response_code', [
        ('superuser', 302),
        ('user_admin', 302),
        ('user', 404),
        ('other_admin', 404),
        ('anonymous_user', 302),
    ])
    def test_rule_delete_access(self, request, client, org_rule, user_fixture, response_code):
        """For POST-requests, allowed access is answered with a 302 redirect."""

        user = request.getfixturevalue(user_fixture)

        response = self.post_rule_delete(client, user, org_rule.pk)

        assert response.status_code == response_code

    def test_rule_delete(self, client, user_admin, test_org, rule_data, org_rule):

        self.post_rule_delete(client, user_admin, org_rule.pk)

        assert CustomRule.objects.filter(pk=org_rule.pk).exists() is False

    def post_rule_delete(self, client, user, pk, **kwargs):
        if not isinstance(user, AnonymousUser):
            client.force_login(user)
        response = client.post(
            reverse_lazy('customrule_delete', kwargs={'pk': pk}))
        return response


@pytest.mark.django_db
class TestCustomRuleConnect:

    @pytest.mark.parametrize('user_fixture,response_code', [
        ('superuser', 200),
        ('user_admin', 200),
        ('other_admin', 404),
        ('user', 404),
        ('anonymous_user', 302),
    ])
    def test_rule_connect_access(
            self,
            request,
            client,
            org_rule,
            test_org,
            user_fixture,
            response_code):

        user = request.getfixturevalue(user_fixture)

        response = self.post_rule_connect(
            client, user, org_rule.pk, {
                "selected_org": test_org.uuid})

        assert response.status_code == response_code

    def test_connect_organization_to_rule(self, client, org_rule, test_org, user_admin):

        self.post_rule_connect(
            client, user_admin, org_rule.pk, {
                "selected_org": test_org.uuid, "table-checkbox": org_rule.pk})

        assert org_rule.organizations.filter(uuid=test_org.uuid).exists()

    def test_disconnect_organization_from_rule(self, client, org_rule, test_org, user_admin):

        org_rule.organizations.add(test_org)

        self.post_rule_connect(
            client, user_admin, org_rule.pk, {
                "selected_org": test_org.uuid, "table-checkbox": 0})

        assert org_rule.organizations.filter(uuid=test_org.uuid).exists() is False

    def post_rule_connect(self, client, user, pk, data, **kwargs):
        if not isinstance(user, AnonymousUser):
            client.force_login(user)
        response = client.post(
            reverse_lazy('connect-rule-to-org', kwargs={'pk': pk}), data)
        return response
