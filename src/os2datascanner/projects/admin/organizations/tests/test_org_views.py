import pytest

from django.contrib.auth.models import Permission
from django.urls import reverse_lazy

from ..models import Organization, Position, OrganizationalUnit

from os2datascanner.core_organizational_structure.models.organization import (
    StatisticsPageConfigChoices, DPOContactChoices, SupportContactChoices, OutlookCategorizeChoices,
    LeaderTabConfigChoices, SBSYSTabConfigChoices)


@pytest.mark.django_db
class TestOrganizationListViews:
    def test_superuser_list(self, client, superuser, test_client, other_client):
        """Superusers should be able to see all clients."""
        client.force_login(superuser)

        url = reverse_lazy("organization-list")
        response = client.get(url)

        assert response.status_code == 200
        assert test_client in response.context.get("client_list")
        assert other_client in response.context.get("client_list")

    def test_administrator_with_permission_list(self, client, user_admin,
                                                test_client, other_client):
        """Users with the "view_client"-permission should be able to see
        all clients."""
        client.force_login(user_admin)
        user_admin.user_permissions.add(
                Permission.objects.get(codename="view_client"))

        url = reverse_lazy("organization-list")
        response = client.get(url)

        assert response.status_code == 200
        assert test_client in response.context.get("client_list")
        assert other_client in response.context.get("client_list")

    def test_administrator_for_list(self, client, user_admin, test_client, other_client):
        """Administrators should only be able to see the client, that they are
        administrator for."""

        client.force_login(user_admin)

        url = reverse_lazy("organization-list")

        response = client.get(url)

        assert response.status_code == 200
        assert test_client in response.context.get("client_list")
        assert other_client not in response.context.get("client_list")

    def test_regular_user_list(self, client, user, test_client, other_client):
        """A user which is neither Administrator or superuser should not be
        able to see anything."""
        client.force_login(user)

        url = reverse_lazy("organization-list")

        response = client.get(url)

        assert test_client not in response.context.get("client_list")
        assert other_client not in response.context.get("client_list")


@pytest.mark.django_db
class TestAddOrganizationViews:

    def test_superuser_create_unique_name_organization(self, client, superuser, test_client):
        """Successfully creating an organization redirects to the list view."""
        client.force_login(superuser)
        num_org_pre = Organization.objects.count()
        url = reverse_lazy('add-organization-for',
                           kwargs={'client_id': test_client.uuid})
        response = client.post(url, {
            'name': 'Unique',
            'contact_email': 'test@unique.mail',
            'contact_phone': '12341234',
        })

        success_url = reverse_lazy('organization-list')
        num_org_post = Organization.objects.count()
        new_org = Organization.objects.get(name="Unique")
        expected_code = 302

        assert response.status_code == expected_code
        assert response["Location"] == success_url
        assert num_org_post == num_org_pre + 1
        assert new_org.contact_email == "test@unique.mail"
        assert new_org.contact_phone == "12341234"
        assert new_org.client == test_client

    def test_superuser_create_same_name_organization(self, client, superuser, test_client):
        """Providing a name already in use for an organization
        should invalidate the form and display an error."""
        client.force_login(superuser)
        Organization.objects.create(name='Same', slug='same', client=test_client)
        num_org_pre = Organization.objects.count()
        url = reverse_lazy('add-organization-for', kwargs={'client_id': test_client.uuid})
        response = client.post(url, {
            'name': 'Same',
            'contact_email': '',
            'contact_phone': '',
        })

        num_org_post = Organization.objects.count()
        expected_code = 200

        assert response.status_code == expected_code
        assert num_org_post == num_org_pre
        assert 'form' in response.context
        assert 'name' in response.context['form'].errors

    def test_blank_user_create_organization(self, client, user, test_client):
        """A user with no permission should not be able to create a new organization."""
        client.force_login(user)
        num_org_pre = Organization.objects.count()
        url = reverse_lazy('add-organization-for',
                           kwargs={'client_id': test_client.uuid})
        response = client.post(url, {
            'name': 'New Org',
            'contact_email': 'test@unique.mail',
            'contact_phone': '12341234',
        })

        num_org_post = Organization.objects.count()
        expected_code = 403

        assert response.status_code == expected_code
        assert num_org_post == num_org_pre
        assert not Organization.objects.filter(name="New Org").exists()

    def test_administrator_create_organization_not_permitted(
            self, client, user_admin, test_client, other_client):
        """An administrator for one client should not be able to create a new
        organization for another client."""
        client.force_login(user_admin)
        num_org_pre = Organization.objects.count()
        url = reverse_lazy('add-organization-for',
                           kwargs={'client_id': other_client.uuid})
        response = client.post(url, {
            'name': 'New Org',
            'contact_email': 'test@unique.mail',
            'contact_phone': '12341234',
        })

        num_org_post = Organization.objects.count()
        expected_code = 403

        assert response.status_code == expected_code
        assert num_org_post == num_org_pre
        assert not Organization.objects.filter(name="New Org").exists()

    def test_administrator_create_organization_permitted(self, client, user_admin, test_client):
        """An administrator for a client should be able to create a new
        organization for that client."""
        client.force_login(user_admin)

        # User needs correct permission to do this
        user_admin.user_permissions.add(Permission.objects.get(codename="add_organization"))

        num_org_pre = Organization.objects.count()
        url = reverse_lazy('add-organization-for',
                           kwargs={'client_id': test_client.uuid})
        response = client.post(url, {
            'name': 'New Org',
            'contact_email': 'test@unique.mail',
            'contact_phone': '12341234',
        })

        success_url = reverse_lazy('organization-list')
        num_org_post = Organization.objects.count()
        new_org = Organization.objects.get(name="New Org")
        expected_code = 302

        assert response.status_code == expected_code
        assert response["Location"] == success_url
        assert num_org_post == num_org_pre + 1
        assert new_org.contact_email == "test@unique.mail"
        assert new_org.contact_phone == "12341234"
        assert new_org.client == test_client

    def test_administrator_create_organization_no_permission(self, client, user_admin, test_client):
        """Administrators should not be able to create an organization without
        the "add_organization"-permission."""
        client.force_login(user_admin)

        url = reverse_lazy('add-organization-for',
                           kwargs={'client_id': test_client.uuid})
        response = client.post(url, {
            'name': 'New Org',
            'contact_email': 'test@unique.mail',
            'contact_phone': '12341234',
        })

        assert response.status_code == 403


@pytest.mark.django_db
class TestUpdateOrganizationViews:

    def test_blank_user_updating_an_organization(self, client, user, test_org):
        """Users who are not administrators should not be able to update any
        organizations."""
        client.force_login(user)

        # User needs the correct permission to do this
        user.user_permissions.add(Permission.objects.get(codename="change_organization"))

        url = reverse_lazy('edit-organization', kwargs={'slug': test_org.slug})
        response = client.post(url, {
            'name': 'Updated Organization',
            'contact_email': 'something@else.com',
            'contact_phone': 'new phone, who dis?',
        })

        expected_code = 404

        assert response.status_code == expected_code
        assert not Organization.objects.filter(name="Updated Organization").exists()

    def test_administrator_updating_an_organization_permitted(self, client, user_admin, test_org):
        """An administrator should be able to edit an organization owned by
        the client, that the user is administrator for."""
        client.force_login(user_admin)

        # User needs correct permission to do this
        user_admin.user_permissions.add(Permission.objects.get(codename="change_organization"))

        num_org_pre = Organization.objects.count()
        url = reverse_lazy('edit-organization', kwargs={'slug': test_org.slug})
        response = client.post(url, {
            'name': 'Updated Organization',
            'contact_email': 'something@else.com',
            'contact_phone': 'new phone, who dis?',
            'leadertab_access': StatisticsPageConfigChoices.MANAGERS,
            'dpotab_access': StatisticsPageConfigChoices.DPOS,
            'show_support_button': False,
            'support_contact_method': SupportContactChoices.NONE,
            'support_name': 'IT',
            'support_value': '',
            'dpo_contact_method': DPOContactChoices.NONE,
            'dpo_name': '',
            'dpo_value': '',
            'outlook_categorize_email_permission': OutlookCategorizeChoices.NONE,
            'outlook_delete_email_permission': False,
            'onedrive_delete_permission': False,
            'synchronization_time': "17:00",
            'leadertab_config': LeaderTabConfigChoices.BOTH,
            'sbsystab_access': SBSYSTabConfigChoices.NONE
        })

        success_url = reverse_lazy('organization-list')
        num_org_post = Organization.objects.count()
        test_org.refresh_from_db()
        expected_code = 302

        assert response.status_code == expected_code
        assert response["Location"] == success_url
        assert num_org_post == num_org_pre
        assert test_org.name == "Updated Organization"
        assert test_org.contact_email == "something@else.com"
        assert test_org.contact_phone == "new phone, who dis?"

    def test_administrator_updating_an_organization_not_permitted(
            self, client, user_admin, other_org):
        """An administrator should not be able to edit an organization owned by
        another client, than the one the user is administrator for."""
        client.force_login(user_admin)

        # User needs correct permission to do this
        user_admin.user_permissions.add(Permission.objects.get(codename="change_organization"))

        url = reverse_lazy('edit-organization', kwargs={'slug': other_org.slug})
        response = client.post(url, {
            'name': 'Updated Organization',
            'contact_email': 'something@else.com',
            'contact_phone': 'new phone, who dis?',
            'msgraph_write_permissions': '',
        })

        other_org.refresh_from_db()
        expected_code = 404

        assert response.status_code == expected_code
        assert other_org.name != "Updated Organization"

    def test_administrator_updating_an_organization_no_permission(
            self, client, user_admin, test_org):
        """An administrator should not be able to edit an organization if they
        do not have the "change_organization"-permission."""
        client.force_login(user_admin)
        url = reverse_lazy('edit-organization', kwargs={'slug': test_org.slug})
        response = client.post(url, {
            'name': 'Updated Organization',
            'contact_email': 'something@else.com',
            'contact_phone': 'new phone, who dis?',
            'leadertab_access': StatisticsPageConfigChoices.MANAGERS,
            'dpotab_access': StatisticsPageConfigChoices.DPOS,
            'show_support_button': False,
            'support_contact_method': SupportContactChoices.NONE,
            'support_name': 'IT',
            'support_value': '',
            'dpo_contact_method': DPOContactChoices.NONE,
            'dpo_name': '',
            'dpo_value': '',
            'outlook_categorize_email_permission': OutlookCategorizeChoices.NONE,
            'outlook_delete_email_permission': False,
            'onedrive_delete_permission': False,
            'synchronization_time': "17:00",
            'leadertab_config': LeaderTabConfigChoices.BOTH,
            'sbsystab_access': SBSYSTabConfigChoices.NONE
        })

        assert response.status_code == 403

    def test_superuser_updating_an_organization(self, client, superuser, test_org):
        """Superusers should be able to update all organizations."""
        client.force_login(superuser)
        num_org_pre = Organization.objects.count()
        url = reverse_lazy('edit-organization', kwargs={'slug': test_org.slug})
        response = client.post(url, {
            'name': 'Updated Organization',
            'contact_email': 'something@else.com',
            'contact_phone': 'new phone, who dis?',
            'leadertab_access': StatisticsPageConfigChoices.MANAGERS,
            'dpotab_access': StatisticsPageConfigChoices.DPOS,
            'show_support_button': False,
            'support_contact_method': SupportContactChoices.NONE,
            'support_name': 'IT',
            'support_value': '',
            'dpo_contact_method': DPOContactChoices.NONE,
            'dpo_name': '',
            'dpo_value': '',
            'outlook_categorize_email_permission': OutlookCategorizeChoices.NONE,
            'outlook_delete_email_permission': False,
            'onedrive_delete_permission': False,
            'synchronization_time': "17:00",
            'leadertab_config': LeaderTabConfigChoices.BOTH,
            'sbsystab_access': SBSYSTabConfigChoices.NONE
        })

        success_url = reverse_lazy('organization-list')
        num_org_post = Organization.objects.count()
        test_org.refresh_from_db()
        expected_code = 302

        assert response.status_code == expected_code
        assert response["Location"] == success_url
        assert num_org_post == num_org_pre
        assert test_org.name == "Updated Organization"
        assert test_org.contact_email == "something@else.com"
        assert test_org.contact_phone == "new phone, who dis?"


@pytest.mark.django_db
class TestDeleteOrganizationViews:

    def test_blank_user_delete_organization(self, client, user, test_org):
        """Trying to delete an organization as a user with no permissions at
        all should fail."""
        client.force_login(user)
        num_org_pre = Organization.objects.count()
        url = reverse_lazy('delete-organization', kwargs={'slug': test_org.slug})
        response = client.post(url)

        num_org_post = Organization.objects.count()
        expected_code = 403

        assert response.status_code == expected_code
        assert num_org_post == num_org_pre

    def test_administrator_delete_organization(self, client, user_admin, test_org):
        """Trying to delete an organization as an administrator for the client
        should fail."""
        client.force_login(user_admin)
        num_org_pre = Organization.objects.count()
        url = reverse_lazy('delete-organization', kwargs={'slug': test_org.slug})
        response = client.post(url)

        num_org_post = Organization.objects.count()
        expected_code = 403

        assert response.status_code == expected_code
        assert num_org_post == num_org_pre

    def test_superuser_delete_organization(self, client, superuser, test_org):
        """Trying to delete an organization as a superuser should succeed."""
        client.force_login(superuser)
        num_org_pre = Organization.objects.count()
        url = reverse_lazy('delete-organization', kwargs={'slug': test_org.slug})
        response = client.post(url)

        success_url = reverse_lazy('organization-list')
        num_org_post = Organization.objects.count()
        expected_code = 302

        assert response.status_code == expected_code
        assert response["Location"] == success_url
        assert num_org_post == num_org_pre - 1
        assert not Organization.objects.filter(name='test_org').exists()


@pytest.mark.django_db
class TestOrganizationalUnitListView:

    def test_superuser_list(
            self,
            client,
            superuser,
            test_org,
            test_org2,
            familien_sand,
            dansk_kartoffelavlerforening,
            oluf,
            gertrud,
            olsen_banden,
            børges_værelse,
            egon):
        """Superusers should be able to see all organizational units."""
        client.force_login(superuser)

        # Add accounts to ous
        # Familien Sand already contains oluf and gertrud
        dansk_kartoffelavlerforening.account_set.add(oluf)
        olsen_banden.account_set.add(egon)

        # URL to all units from organization 1
        url1 = reverse_lazy("orgunit-list", kwargs={'org_slug': test_org.slug})
        # URL to all units from organization 2
        url2 = reverse_lazy("orgunit-list", kwargs={'org_slug': test_org2.slug})

        # This response should yield two units
        response1 = client.get(url1)
        # This response should yield one unit, as the other one has no accounts associated
        response2 = client.get(url2)
        # This response should yield two units, including one empty
        response3 = client.get(url2, {"show_empty": "on"})

        assert response1.status_code == 200
        assert response2.status_code == 200
        assert response3.status_code == 200
        assert len(response1.context.get("object_list")) == 2
        assert len(response2.context.get("object_list")) == 1
        assert len(response3.context.get("object_list")) == 2
        assert familien_sand in response1.context.get("object_list")
        assert dansk_kartoffelavlerforening in response1.context.get("object_list")
        assert olsen_banden in response2.context.get("object_list")
        assert børges_værelse not in response2.context.get("object_list")
        assert olsen_banden in response3.context.get("object_list")
        assert børges_værelse in response3.context.get("object_list")

    def test_administrator_for_list(
            self,
            client,
            user_admin,
            test_org,
            test_org2,
            familien_sand,
            dansk_kartoffelavlerforening,
            oluf,
            gertrud,
            olsen_banden,
            børges_værelse,
            egon,
            test_client,
            other_client):
        """Administrators should be able to see the units belonging to
        organizations, belonging to clients, for which they are
        administrators."""
        # Add user permission
        user_admin.user_permissions.add(Permission.objects.get(codename="view_organizationalunit"))

        client.force_login(user_admin)

        # Add accounts to ous
        # Familien Sand already contains oluf and gertrud
        dansk_kartoffelavlerforening.account_set.add(oluf)
        olsen_banden.account_set.add(egon)

        # URL to all units from organization 1
        url1 = reverse_lazy("orgunit-list", kwargs={'org_slug': test_org.slug})
        # URL to all units from organization 2
        url2 = reverse_lazy("orgunit-list", kwargs={'org_slug': test_org2.slug})

        # This response should yield two units
        response1 = client.get(url1)
        # The user should not be able to access this, as it belongs to a different client
        response2 = client.get(url2)

        assert response1.status_code == 200
        assert response2.status_code == 404
        assert len(response1.context.get("object_list")) == 2
        assert familien_sand in response1.context.get("object_list")
        assert dansk_kartoffelavlerforening in response1.context.get("object_list")

    def test_regular_user_list(self, client, user, test_org, test_org2):
        """Users with no priviliges should not be able to see any units."""
        # Add user permission
        user.user_permissions.add(Permission.objects.get(codename="view_organizationalunit"))

        client.force_login(user)

        # URL to all units from organization 1
        url1 = reverse_lazy("orgunit-list", kwargs={'org_slug': test_org.slug})
        # URL to all units from organization 2
        url2 = reverse_lazy("orgunit-list", kwargs={'org_slug': test_org2.slug})

        response1 = client.get(url1)
        response2 = client.get(url2)

        assert response1.status_code == 404
        assert response2.status_code == 404


@pytest.mark.django_db
class TestOrganizationalUnitListViewAddRemoveManagers:

    def test_add_manager_superuser(
            self,
            client,
            superuser,
            test_org,
            test_org2,
            fritz,
            nisserne,
            egon,
            olsen_banden):
        """A superuser should be able to add managers."""
        client.force_login(superuser)

        # URL to all units from organization 1
        url1 = reverse_lazy("orgunit-list", kwargs={'org_slug': test_org.slug})
        # URL to all units from organization 2
        url2 = reverse_lazy("orgunit-list", kwargs={'org_slug': test_org2.slug})

        response1 = client.post(
            url1, {"add-manager": fritz.uuid, "orgunit": nisserne.pk})
        response2 = client.post(
            url2, {"add-manager": egon.uuid, "orgunit": olsen_banden.pk})

        assert response1.status_code == 200
        assert response2.status_code == 200
        assert nisserne in fritz.get_managed_units()
        assert olsen_banden in egon.get_managed_units()

    def test_remove_manager_superuser(
            self,
            client,
            superuser,
            test_org,
            test_org2,
            fritz,
            nisserne,
            egon,
            olsen_banden):
        """A superuser should be able to remove managers from all units."""
        client.force_login(superuser)

        Position.managers.create(account=fritz, unit=nisserne)
        Position.managers.create(account=egon, unit=olsen_banden)

        # URL to all units from organization 1
        url1 = reverse_lazy("orgunit-list", kwargs={'org_slug': test_org.slug})
        # URL to all units from organization 2
        url2 = reverse_lazy("orgunit-list", kwargs={'org_slug': test_org2.slug})

        response1 = client.post(
            url1, {"rem-manager": fritz.uuid, "orgunit": nisserne.pk})
        response2 = client.post(
            url2, {"rem-manager": egon.uuid, "orgunit": olsen_banden.pk})

        assert response1.status_code == 200
        assert response2.status_code == 200
        assert nisserne not in fritz.get_managed_units()
        assert olsen_banden not in egon.get_managed_units()

    def test_add_manager_administrator(
            self,
            client,
            user_admin,
            test_org,
            test_org2,
            fritz,
            nisserne,
            egon,
            olsen_banden):
        """An administrator should be able to add managers to units they are
        administrator for."""
        # Add user permission
        user_admin.user_permissions.add(Permission.objects.get(codename="view_organizationalunit"))

        client.force_login(user_admin)

        # URL to all units from organization 1
        url1 = reverse_lazy("orgunit-list", kwargs={'org_slug': test_org.slug})
        # URL to all units from organization 2
        url2 = reverse_lazy("orgunit-list", kwargs={'org_slug': test_org2.slug})

        response1 = client.post(
            url1, {"add-manager": fritz.uuid, "orgunit": nisserne.pk})
        response2 = client.post(
            url2, {"add-manager": egon.uuid, "orgunit": olsen_banden.pk})

        assert response1.status_code == 200
        assert response2.status_code == 404
        assert nisserne in fritz.get_managed_units()
        assert olsen_banden not in egon.get_managed_units()

    def test_remove_manager_administrator(
            self,
            client,
            user_admin,
            test_org,
            test_org2,
            fritz,
            nisserne,
            egon,
            olsen_banden):
        """An administrator should be able to remove managers from the units
        they are administrators for."""
        # Add user permission
        user_admin.user_permissions.add(Permission.objects.get(codename="view_organizationalunit"))

        client.force_login(user_admin)

        Position.managers.create(account=fritz, unit=nisserne)
        Position.managers.create(account=egon, unit=olsen_banden)

        # URL to all units from organization 1
        url1 = reverse_lazy("orgunit-list", kwargs={'org_slug': test_org.slug})
        # URL to all units from organization 2
        url2 = reverse_lazy("orgunit-list", kwargs={'org_slug': test_org2.slug})

        response1 = client.post(
            url1, {"rem-manager": fritz.uuid, "orgunit": nisserne.pk})
        response2 = client.post(
            url2, {"rem-manager": egon.uuid, "orgunit": olsen_banden.pk})

        assert response1.status_code == 200
        assert response2.status_code == 404
        assert nisserne not in fritz.get_managed_units()
        assert olsen_banden in egon.get_managed_units()

    def test_add_manager_regular_user(
            self,
            client,
            user,
            test_org,
            test_org2,
            fritz,
            nisserne,
            egon,
            olsen_banden):
        """An unprivileged user should not be able to add managers to any
        units."""
        # Add user permission
        user.user_permissions.add(Permission.objects.get(codename="view_organizationalunit"))

        client.force_login(user)

        # URL to all units from organization 1
        url1 = reverse_lazy("orgunit-list", kwargs={'org_slug': test_org.slug})
        # URL to all units from organization 2
        url2 = reverse_lazy("orgunit-list", kwargs={'org_slug': test_org2.slug})

        response1 = client.post(
            url1, {"add-manager": fritz.uuid, "orgunit": nisserne.pk})
        response2 = client.post(
            url2, {"add-manager": egon.uuid, "orgunit": olsen_banden.pk})

        assert response1.status_code == 404
        assert response2.status_code == 404
        assert nisserne not in fritz.get_managed_units()
        assert olsen_banden not in egon.get_managed_units()

    def test_remove_manager_regular_user(
            self,
            client,
            user,
            test_org,
            test_org2,
            fritz,
            nisserne,
            egon,
            olsen_banden):
        """An unprivileged user should not be able to remove managers from
        any units."""
        # Add user permission
        user.user_permissions.add(Permission.objects.get(codename="view_organizationalunit"))

        client.force_login(user)

        Position.managers.create(account=fritz, unit=nisserne)
        Position.managers.create(account=egon, unit=olsen_banden)

        # URL to all units from organization 1
        url1 = reverse_lazy("orgunit-list", kwargs={'org_slug': test_org.slug})
        # URL to all units from organization 2
        url2 = reverse_lazy("orgunit-list", kwargs={'org_slug': test_org2.slug})

        response1 = client.post(
            url1, {"rem-manager": fritz.uuid, "orgunit": nisserne.pk})
        response2 = client.post(
            url2, {"rem-manager": egon.uuid, "orgunit": olsen_banden.pk})

        assert response1.status_code == 404
        assert response2.status_code == 404
        assert nisserne in fritz.get_managed_units()
        assert olsen_banden in egon.get_managed_units()


@pytest.mark.django_db
class TestOrganizationalUnitVisibilityView:
    headers = {"HTTP_HX-Request": "true"}

    def test_orgunit_visibility_access_as_superuser(self, client, superuser, test_org):
        """Superusers should have access to the view."""
        client.force_login(superuser)
        url = reverse_lazy("edit-orgunit-visibility-view", kwargs={"org_slug": test_org.slug})
        response = client.get(url)

        assert response.status_code == 200

    def test_orgunit_visibility_access_as_administrator(self, client, user_admin, test_org):
        """Superusers should have access to the view."""
        user_admin.user_permissions.add(
                Permission.objects.get(codename="change_visibility_organizationalunit"))
        client.force_login(user_admin)
        url = reverse_lazy("edit-orgunit-visibility-view", kwargs={"org_slug": test_org.slug})
        response = client.get(url)

        assert response.status_code == 200

    def test_orgunit_visibility_access_as_user(self, client, user, test_org):
        """Superusers should have access to the view."""
        user.user_permissions.add(
                Permission.objects.get(codename="change_visibility_organizationalunit"))
        client.force_login(user)
        url = reverse_lazy("edit-orgunit-visibility-view", kwargs={"org_slug": test_org.slug})
        response = client.get(url)

        assert response.status_code == 404

    @pytest.mark.parametrize("has_perm", [True, False])
    def test_orgunit_visibility_access_permission(self, client, user_admin, has_perm, test_org):
        if has_perm:
            user_admin.user_permissions.add(
                Permission.objects.get(codename="change_visibility_organizationalunit"))
        client.force_login(user_admin)

        url = reverse_lazy("edit-orgunit-visibility-view", kwargs={"org_slug": test_org.slug})

        response = client.get(url)

        if has_perm:
            assert response.status_code == 200
        else:
            assert response.status_code == 403

    def test_toggle_orgunit_visibility(self, client, user_admin, test_org, familien_sand,
                                       dansk_kartoffelavlerforening):
        user_admin.user_permissions.add(
            Permission.objects.get(codename="change_visibility_organizationalunit"))
        client.force_login(user_admin)

        url = reverse_lazy("edit-orgunit-visibility-view", kwargs={"org_slug": test_org.slug})

        headers = self.headers
        headers["HTTP_HX-Trigger-Name"] = "toggle_orgunit_hidden_state"

        # Check visibility of org unit before POST
        state = familien_sand.hidden

        response = client.post(url, data={"pk": familien_sand.pk}, **headers)

        assert response.status_code == 200

        # Orgunit visibility should be reversed
        familien_sand.refresh_from_db()
        assert familien_sand.hidden != state

    def test_hide_all_orgunits(self, client, user_admin, test_org, familien_sand,
                               dansk_kartoffelavlerforening):
        user_admin.user_permissions.add(
            Permission.objects.get(codename="change_visibility_organizationalunit"))
        client.force_login(user_admin)

        url = reverse_lazy("edit-orgunit-visibility-view", kwargs={"org_slug": test_org.slug})

        headers = self.headers
        headers["HTTP_HX-Trigger-Name"] = "hide_all_orgunits"

        # Make sure all orgunits are unhidden before sending POST
        OrganizationalUnit.objects.update(hidden=False)

        response = client.post(url, data={}, **headers)

        assert response.status_code == 200

        assert not OrganizationalUnit.objects.filter(hidden=False).exists()

    def test_unhide_all_orgunits(self, client, user_admin, test_org, familien_sand,
                                 dansk_kartoffelavlerforening):
        user_admin.user_permissions.add(
            Permission.objects.get(codename="change_visibility_organizationalunit"))
        client.force_login(user_admin)

        url = reverse_lazy("edit-orgunit-visibility-view", kwargs={"org_slug": test_org.slug})

        headers = self.headers
        headers["HTTP_HX-Trigger-Name"] = "unhide_all_orgunits"

        # Make sure all orgunits are unhidden before sending POST
        OrganizationalUnit.objects.update(hidden=True)

        response = client.post(url, data={}, **headers)

        assert response.status_code == 200

        assert not OrganizationalUnit.objects.filter(hidden=True).exists()
