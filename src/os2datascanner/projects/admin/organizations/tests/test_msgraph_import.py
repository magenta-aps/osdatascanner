import datetime
import pytest
from copy import deepcopy
from os2datascanner.projects.admin.import_services.models import MSGraphConfiguration
from ..models import Account, OrganizationalUnit, Alias, Position
from .. import msgraph_import_actions


@pytest.mark.django_db
class TestMSGraphImport:

    @pytest.fixture(autouse=True)
    def graph_import_config(self, test_org):
        return MSGraphConfiguration.objects.create(organization=test_org,
                                                   hide_units_on_import=False,
                                                   last_modified=datetime.datetime(
                                                       2025, 9, 2, 12,
                                                       0, 0,
                                                       tzinfo=datetime.timezone.utc)
                                                   )

    @pytest.fixture()
    def TEST_CORP(self):
        return [
            {
                "uuid": "37c7aa4e-b884-4f77-9f44-b233237de630",
                "name": "Subgroup to Vejstrand",
                "members": [
                    {
                        "type": "user",
                        "uuid": "118e5d18-90ba-4150-a11c-9162c24bb5ce",
                        "givenName": "Charles",
                        "surname": "Darwin",
                        "userPrincipalName": "Charles@darwindomain.onmicrosoft.com",
                        "email": "Charles@darwindomain.onmicrosoft.com"
                    }
                ]
            },
            {
                "uuid": "64116cda-5c3c-4e32-b5a2-01cea0be9888",
                "name": "Casuals Golf Club",
                "members": [
                    {
                        "type": "user",
                        "uuid": "3382c90d-9646-4562-9f47-3994957030a6",
                        "givenName": "Albert",
                        "surname": "Twostones",
                        "userPrincipalName": "albert@darwindomain.onmicrosoft.com",
                        "sid": "S-1-5-21-1004336348-1177238915-682003330-512"
                    },
                    {
                        "type": "user",
                        "uuid": "118e5d18-90ba-4150-a11c-9162c24bb5ce",
                        "givenName": "Charles",
                        "surname": "Darwin",
                        "userPrincipalName": "Charles@darwindomain.onmicrosoft.com",
                        "email": "Charles@darwindomain.onmicrosoft.com",
                    },
                ]
            },
            {
                "uuid": "7e6bc04d-15c1-420b-999d-c12581520c23",
                "name": "Vejstrand",
                "members": [
                    {
                        "type": "user",
                        "uuid": "118e5d18-90ba-4150-a11c-9162c24bb5ce",
                        "givenName": "Charles",
                        "surname": "Darwin",
                        "userPrincipalName": "Charles@darwindomain.onmicrosoft.com",
                        "email": "Charles@darwindomain.onmicrosoft.com"
                    },
                    {
                        "type": "group",
                        "uuid": "37c7aa4e-b884-4f77-9f44-b233237de630",
                        "displayName": "Subgroup to Vejstrand"
                    },
                    {
                        "type": "user",
                        "uuid": "93f2f74e-3811-476f-ac56-e7f0d3007fcc",
                        "givenName": "Guy",
                        "surname": "Average",
                        "userPrincipalName": "guy@darwindomain.onmicrosoft.com",
                        "email": "guy@darwindomain.onmicrosoft.com"
                    }
                ]
            },
            # Cases of no UPN have been observed and will cause database integrity error.
            # We use it as username -- and to have an account, that is the bare minimum.
            # Hence, if missing, we should not try to create the account.
            {
                "uuid": "78111cda-2c4c-4k32-b5a2-01cea0be1337",
                "name": "Group where user has no UPN",
                "members": [
                    {
                        "type": "user",
                        "uuid": "1111c11d-1111-1111-1f11-1111111111a1",
                        "givenName": "Cousin",
                        "surname": "Guf",
                        "userPrincipalName": None,
                    }
                ]
            }
        ]

    @pytest.fixture(autouse=True)
    def import_run(self, test_org, TEST_CORP, settings):
        # Running with immediate constraints off
        # test_account_changed_uuid will/should fail, without it-
        # our dev-env has this setting true, but default and CI-test settings are false.
        settings.PREPNPUB_IMMEDIATE_CONSTRAINTS = False
        # Import from json
        msgraph_import_actions.perform_msgraph_import(
            TEST_CORP, test_org
        )

    def test_ou_import(self, TEST_CORP):
        """ Importing should create corresponding OU's from JSON"""
        all_uuids = set()
        for ou in TEST_CORP:
            all_uuids.add(ou["uuid"])

        imported_ids = OrganizationalUnit.objects.values("imported_id")

        for imp_id in imported_ids:
            assert (imp_id["imported_id"] in list(all_uuids)), "Not all OU's were created!"

        # Should be no hidden units.
        assert not OrganizationalUnit.objects.filter(hidden=True).exists()

    def test_import_new_ou_hidden_default(self, TEST_CORP, test_org, graph_import_config):

        # Arrange: Add a new OU and update configuration
        TEST_CORP.append(
            {
                "uuid": "11a1aa1a-a111-1f11-1a11-a111111aa111",
                "name": "Hide and seekers",
                "members": [
                    {
                        "type": "user",
                        "uuid": "998e5d18-90ba-4150-a11c-1234c24bb5ce",
                        "givenName": "Casper",
                        "surname": "Ghost",
                        "userPrincipalName": "Casper@Ghost.onmicrosoft.com",
                        "email": "Casper@Ghost.onmicrosoft.com"
                        }
                    ]
                })

        graph_import_config.hide_units_on_import = True
        graph_import_config.save()

        # Act: Run import
        msgraph_import_actions.perform_msgraph_import(
            TEST_CORP, test_org
        )

        # Assert: Verify the newly imported unit is hidden and existing ones aren't
        assert OrganizationalUnit.objects.filter(name="Hide and seekers", hidden=True).exists()
        assert OrganizationalUnit.objects.filter(hidden=False).exists()

    def test_account_import(self, TEST_CORP):
        """ Importing should create corresponding account objects """

        all_uuids = set()
        for ou in TEST_CORP:
            for member in ou["members"]:
                if member["type"] == "user" and member.get("userPrincipalName") is not None:
                    all_uuids.add(member["uuid"])

        imported_ids = Account.objects.values("imported_id")

        for imp_id in imported_ids:
            assert (imp_id["imported_id"] in list(all_uuids)), "Not all accounts were created!"

    def test_create_positions(self, TEST_CORP):
        """ Accounts and connected positions should be created """

        for ou in TEST_CORP:
            ou_uuid = ou["uuid"]
            for member in ou["members"]:
                if member["type"] == "user" and member.get("userPrincipalName") is not None:
                    ou_obj = OrganizationalUnit.objects.get(imported_id=ou_uuid)
                    acc_obj = Account.objects.get(imported_id=member["uuid"])

                    assert Position.objects.filter(
                        account=acc_obj,
                        unit=ou_obj
                    ).exists(), "No matching position object!"

    def test_create_alias(self, TEST_CORP):
        # Most users have an email and will have an email alias.
        # "Albert Twostones" doesn't have an email, but only an SID
        # He should get an SID-alias (which is also verified here)

        for ou in TEST_CORP:
            for member in ou["members"]:
                if member["type"] == "user" and member.get("userPrincipalName") is not None:
                    member_id = member["uuid"]
                    assert Alias.objects.filter(
                            account__imported_id=member_id
                        ).exists(), "No matching alias object!"

    def test_delete_user(self, TEST_CORP, test_org):
        # Guy Average is being removed
        UPDATED_CORP = deepcopy(TEST_CORP)
        for ou in UPDATED_CORP:
            for i in range(len(ou["members"])):
                if ou["members"][i]["uuid"] == "93f2f74e-3811-476f-ac56-e7f0d3007fcc":
                    del ou["members"][i]

        # Run import again
        msgraph_import_actions.perform_msgraph_import(
            UPDATED_CORP, test_org
        )
        # Now Guy Average and associated Alias+Position should no longer exist.
        assert not Account.objects.filter(
            imported_id="93f2f74e-3811-476f-ac56-e7f0d3007fcc").exists(), "Account not deleted!"

        assert not Position.objects.filter(
            account__imported_id="93f2f74e-3811-476f-ac56-e7f0d3007fcc"
        ).exists(), "Position not deleted!"

        assert not Alias.objects.filter(
                account__imported_id="93f2f74e-3811-476f-ac56-e7f0d3007fcc"
        ).exists(), "Alias not deleted!"

        # The OU he belonged to (Vejstrand) should still exist - it has other members
        assert OrganizationalUnit.objects.filter(
                name="Vejstrand").exists(), "OU shouldn't be deleted in this case!"

    def test_account_attribute_update(self, TEST_CORP, test_org):
        UPDATED_CORP = deepcopy(TEST_CORP)

        # Run import again
        msgraph_import_actions.perform_msgraph_import(
            UPDATED_CORP, test_org
        )

        # Verify he indeed exists after import
        assert Account.objects.filter(
                imported_id="93f2f74e-3811-476f-ac56-e7f0d3007fcc",
                first_name="Guy", last_name="Average").exists()

        # Guy Average changes name to Poul Poulsen
        for ou in UPDATED_CORP:
            for i in range(len(ou["members"])):
                if ou["members"][i]["uuid"] == "93f2f74e-3811-476f-ac56-e7f0d3007fcc":
                    ou["members"][i]["givenName"] = "Poul"
                    ou["members"][i]["surname"] = "Poulsen"
                    break

        # Run import again
        msgraph_import_actions.perform_msgraph_import(
            UPDATED_CORP, test_org
        )

        # Verify changed attributes after import
        assert Account.objects.filter(
                imported_id="93f2f74e-3811-476f-ac56-e7f0d3007fcc",
                first_name="Poul", last_name="Poulsen").exists()

        # ... and not with the old attributes anymore
        assert not Account.objects.filter(
                imported_id="93f2f74e-3811-476f-ac56-e7f0d3007fcc",
                first_name="Guy", last_name="Average").exists()

    def test_account_changed_uuid(self, TEST_CORP, test_org):
        # Observed that sometimes an account can be deactivated/deleted/recreated, to be
        # identical, but of course with a new uuid.
        UPDATED_CORP = deepcopy(TEST_CORP)

        # Guy Average changed uuid
        for ou in UPDATED_CORP:
            for i in range(len(ou["members"])):
                if ou["members"][i]["uuid"] == "93f2f74e-3811-476f-ac56-e7f0d3007fcc":
                    ou["members"][i]["uuid"] = "99x1o23k-3811-476f-ac56-e7f0d1337baa"
                    break

        # Run import again
        msgraph_import_actions.perform_msgraph_import(
            UPDATED_CORP, test_org
        )

        assert not Account.objects.filter(imported_id="93f2f74e-3811-476f-ac56-e7f0d3007fcc",
                                          first_name="Guy", last_name="Average").exists()
        assert Account.objects.filter(imported_id="99x1o23k-3811-476f-ac56-e7f0d1337baa",
                                      first_name="Guy", last_name="Average").exists()
