import pytest
import json

from django.contrib.auth.models import AnonymousUser
from django.urls import reverse_lazy

from ..adminapp.models.rules import CustomRule, RuleCategory


@pytest.fixture
def rule_data(test_org):
    return {
            "name": "dummy rule",
            "description": "this is a dumb dumb dummy rule",
            "sensitivity": 3,
            "rule": '{"type": "regex", "expression": "dummy"}',
            "organization": str(test_org.uuid)
        }


@pytest.fixture
def name_category():
    return RuleCategory.objects.get_or_create(
        name="name"
    )[0]


@pytest.fixture
def address_category():
    return RuleCategory.objects.get_or_create(
        name="address"
    )[0]


@pytest.fixture
def system_rule1(name_category, address_category):
    rule = CustomRule.objects.create(
        name="system_rule1",
        description="system_rule1",
        sensitivity=1,
        _rule='{"type": "regex", "expression": "dummy"}'
    )
    rule.categories.add(name_category, address_category)
    return rule


@pytest.fixture
def system_rule2(name_category):
    rule = CustomRule.objects.create(
        name="system_rule2",
        description="system_rule2",
        sensitivity=2,
        _rule='{"type": "regex", "expression": "dummy"}'
    )
    rule.categories.add(name_category)
    return rule


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
        assert json.dumps(created_rule._rule) == rule_data['rule']

    @pytest.mark.parametrize('exceptions,valid', [
        ('abc', False),
        ('1111111118', True),
        ('1111111118,1111111119', True),
        ('1111111118, 1111111119', False),
        ('', True),
        ('1111111118;1111111119', False),
    ])
    def test_cprrule_exceptions(self, client, user_admin, rule_data, exceptions, valid):

        rule_data['rule'] = json.dumps({
            "type": "cpr",
            "modulus_11": True,
            "ignore_irrelevant": True,
            "examine_context": True,
            "surrounding_exceptions": "",
            "exceptions": exceptions
        })

        response = self.post_rule_create(client, user_admin, rule_data)

        if valid:
            assert response.status_code == 302
        else:
            assert response.status_code == 200
            assert response.context['form']['rule'].errors

    @pytest.mark.parametrize('surrounding_words,valid', [
        ('abc', True),
        ('abc123', True),
        ('abc123,def456', True),
        ('', True),
        ('yes/no', False),
        ('i_am_mad', False)
    ])
    def test_cprrule_surrounding_words(
            self,
            client,
            user_admin,
            rule_data,
            surrounding_words,
            valid):

        rule_data['rule'] = json.dumps({
            "type": "cpr",
            "modulus_11": True,
            "ignore_irrelevant": True,
            "examine_context": True,
            "exceptions": "",
            "surrounding_exceptions": surrounding_words
        })

        response = self.post_rule_create(client, user_admin, rule_data)

        if valid:
            assert response.status_code == 302
        else:
            assert response.status_code == 200
            assert response.context['form']['rule'].errors

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
        assert json.dumps(updated_rule._rule) == rule_data['rule']

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

    @pytest.mark.parametrize('organization', [
        'test_org',
        'test_org2'
    ])
    def test_connect_organization_to_rule(
            self,
            request,
            client,
            system_rule1,
            organization,
            superuser):

        org = request.getfixturevalue(organization)

        self.post_rule_connect(
            client, superuser, system_rule1.pk, {
                "selected_org": org.uuid, "table-checkbox": system_rule1.pk})

        assert system_rule1.organizations.filter(uuid=org.uuid).exists()

    @pytest.mark.parametrize('organization', [
        'test_org',
        'test_org2'
    ])
    def test_disconnect_organization_from_rule(
            self, request, client, system_rule1, organization, superuser):

        org = request.getfixturevalue(organization)

        system_rule1.organizations.add(org)

        self.post_rule_connect(
            client, superuser, system_rule1.pk, {
                "selected_org": org.uuid, "table-checkbox": 0})

        assert system_rule1.organizations.filter(uuid=org.uuid).exists() is False

    def post_rule_connect(self, client, user, pk, data, **kwargs):
        if not isinstance(user, AnonymousUser):
            client.force_login(user)
        response = client.post(
            reverse_lazy('connect-rule-to-org', kwargs={'pk': pk}), data)
        return response


@pytest.mark.django_db
class TestRuleList:

    def test_available_rules(
            self,
            client,
            user_admin,
            system_rule1,
            system_rule2,
            org_rule,
            org2_rule):

        response = self.get_rule_list(client, user_admin)

        assert response.status_code == 200
        assert org_rule in response.context['customrule_list']
        assert org2_rule not in response.context['customrule_list']
        assert system_rule1 in response.context['systemrule_list']
        assert system_rule2 in response.context['systemrule_list']

    @pytest.mark.parametrize('categories', [
        ['name_category'],
        ['address_category'],
        ['name_category', 'address_category']
    ])
    def test_filtering_by_categories(
            self,
            request,
            client,
            user_admin,
            system_rule1,
            system_rule2,
            categories):
        categories = [request.getfixturevalue(category)
                      for category in categories] if categories else []

        expected_rules = [
            rule for rule in (
                system_rule1,
                system_rule2) if all(
                cat in categories for cat in rule.categories.all())]

        unexpected_rules = [
            rule for rule in (system_rule1, system_rule2) if rule not in expected_rules
        ]

        response = self.get_rule_list(client, user_admin, categories=[cat.pk for cat in categories])

        assert all(rule in response.context['systemrule_list'] for rule in expected_rules)
        assert all(rule not in response.context['systemrule_list'] for rule in unexpected_rules)

    @pytest.mark.parametrize('user_fixture,expected_orgs', [
        ('user_admin', ['test_org']),
        ('other_admin', ['test_org2']),
        ('superuser', ['test_org', 'test_org2']),
    ])
    def test_available_organizations(
            self,
            request,
            client,
            user_fixture,
            expected_orgs,
            test_org,
            test_org2):
        user = request.getfixturevalue(user_fixture)

        expected_orgs = [request.getfixturevalue(org) for org in expected_orgs]

        response = self.get_rule_list(client, user)

        assert all(org in response.context['organizations'] for org in expected_orgs)
        assert all(org in expected_orgs for org in response.context['organizations'])

    def test_available_categories(self, client, user_admin, name_category, address_category):

        response = self.get_rule_list(client, user_admin)

        assert name_category in response.context['categories']
        assert address_category in response.context['categories']

    def get_rule_list(self, client, user, **kwargs):
        if not isinstance(user, AnonymousUser):
            client.force_login(user)
        response = client.get(reverse_lazy('rules'), kwargs)
        return response

    def test_number_of_system_rules_multiple_orgs(
            self, test_org, test_org2, system_rule1, superuser, client):
        """Implemented based on a bug: System rules would show up once for every
        organization, which it was connected to. We only want each system rule
        to show up once."""
        test_org2.system_rules.add(system_rule1)

        response = self.get_rule_list(client, superuser)

        assert len(response.context['systemrule_list']) == 2
        assert response.context['systemrule_list'].order_by("name")[0] != system_rule1
        assert response.context['systemrule_list'].order_by("name")[1] == system_rule1
