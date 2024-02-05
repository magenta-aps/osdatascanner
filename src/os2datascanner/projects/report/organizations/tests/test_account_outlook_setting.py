import pytest
from io import BytesIO

import requests
from requests.models import Response

from ..models import AccountOutlookSetting, OutlookCategory
from ..models.account_outlook_setting import AccountOutlookSettingQuerySet
from ..models.organization import Organization, OutlookCategorizeChoices
from ..models.account import Account


class MockGraphCaller:

    def create_outlook_category(self, *args, **kwargs):
        res = Response()
        res.status_code = 200
        res.raw = BytesIO(b'{ "id" : "a_very_real_category_id" }')
        return res

    def paginated_get(self, *args, **kwargs):
        # This is a bit, mweh.. technically this method can be used for any GET call
        # but in this specific scenario, our response would look like this
        res = [
            {
                "id": "d60ae84c-93b3-45f6-bb74-51ad35d09730",
                "displayName": "OS2datascanner Match",
                "color": "preset15"
            },
            {
                "id": "ad76143b-5180-4751-8079-1f1d3f11b38b",
                "displayName": "OS2datascanner False Positive",
                "color": "preset15"
            }
        ]

        return res

    def delete_category(self, *args, **kwargs):
        res = Response()
        res.status_code = 200
        return res


@pytest.fixture()
def mock_graphcaller(monkeypatch):
    def mock__initiate_graphcaller(*args, **kwargs):
        return MockGraphCaller()

    monkeypatch.setattr(AccountOutlookSettingQuerySet,
                        "_initiate_graphcaller",
                        mock__initiate_graphcaller)


@pytest.mark.django_db
class TestAccountOutlookSetting:

    @classmethod
    def setup_method(cls, mock_graphcaller):
        cls.organization = Organization.objects.create(
            name="Test Organization",
            outlook_categorize_email_permission=OutlookCategorizeChoices.NONE
        )
        cls.organization_org_level = Organization.objects.create(
            name="You shall categorize",
            outlook_categorize_email_permission=OutlookCategorizeChoices.ORG_LEVEL
        )
        cls.organization_ind_level = Organization.objects.create(
            name="Pick your battle",
            outlook_categorize_email_permission=OutlookCategorizeChoices.INDIVIDUAL_LEVEL
        )
        cls.base_account = Account.objects.create(
            username="tandy",
            first_name="Phil",
            last_name="Miller",
            organization=cls.organization
        )

    # AccountOutlookSetting model #
    def test_populate_setting_stores_created_categories(self, mock_graphcaller):
        # Arrange

        # Create an AccountOutlookSetting object
        AccountOutlookSetting.objects.create(account=self.base_account)

        # Act
        AccountOutlookSetting.objects.filter(account=self.base_account).populate_setting()

        # Assert
        self.base_account.refresh_from_db()
        assert (self.base_account.outlook_settings.match_category.category_uuid ==
                "a_very_real_category_id")
        assert (self.base_account.outlook_settings.false_positive_category.category_uuid ==
                "a_very_real_category_id")

    def test_populate_setting_identifies_existing_categories(self, monkeypatch, mock_graphcaller):
        # Arrange

        # Emulate a conflict response.
        def conflict_response(self, *args, **kwargs):
            res = Response()
            res.status_code = 409
            raise requests.HTTPError(response=res)

        monkeypatch.setattr(MockGraphCaller,
                            "create_outlook_category",
                            conflict_response)

        # Create an AccountOutlookSetting object
        AccountOutlookSetting.objects.create(account=self.base_account)

        # Act
        AccountOutlookSetting.objects.filter(account=self.base_account).populate_setting()

        # Assert - ID's should be populated
        self.base_account.refresh_from_db()
        assert (self.base_account.
                outlook_settings.match_category.category_uuid == (
                    "d60ae84c-93b3-45f6-bb74" "-51ad35d09730"))
        assert (self.base_account
                .outlook_settings.false_positive_category.category_uuid == (
                    "ad76143b-5180""-4751-8079""-1f1d3f11b38b")
                )

    def test_bulk_create_populates_with_org_level(self, mock_graphcaller):
        # Arrange
        self.base_account.organization = self.organization_org_level
        self.base_account.save()

        # Act
        AccountOutlookSetting.objects.bulk_create(
            [AccountOutlookSetting(account=self.base_account, categorize_email=True)]
        )

        # Assert
        self.base_account.refresh_from_db()
        assert (self.base_account.outlook_settings.match_category.category_uuid ==
                "a_very_real_category_id")
        assert (self.base_account.outlook_settings.false_positive_category.category_uuid ==
                "a_very_real_category_id")

    def test_bulk_create_doesnt_populate_with_no_permission(self, mock_graphcaller):
        # Arrange

        # Nothing. default org has this disabled.

        # Act
        AccountOutlookSetting.objects.bulk_create(
            [AccountOutlookSetting(account=self.base_account, categorize_email=True)]
        )

        # Assert
        self.base_account.refresh_from_db()
        assert self.base_account.outlook_settings.match_category is None
        assert self.base_account.outlook_settings.false_positive_category is None

    def test_bulk_create_doesnt_populate_with_ind_level(self, mock_graphcaller):
        # Arrange
        self.base_account.organization = self.organization_ind_level
        self.base_account.save()

        # Act
        AccountOutlookSetting.objects.bulk_create(
            [AccountOutlookSetting(account=self.base_account, categorize_email=True)]
        )

        # Assert
        self.base_account.refresh_from_db()
        assert self.base_account.outlook_settings.match_category is None
        assert self.base_account.outlook_settings.false_positive_category is None

    def test_update_colour_identifies_colour_changes(self):
        pass

    def test_delete_categories_removes_uuids_on_ok_response(self, mock_graphcaller):
        # Arrange
        setting = AccountOutlookSetting.objects.create(
                                    account=self.base_account,
                                    categorize_email=True)
        OutlookCategory.objects.create(category_uuid="123",
                                       name=OutlookCategory.OutlookCategoryNames.MATCH,
                                       account_outlook_setting=setting)
        OutlookCategory.objects.create(category_uuid="1234",
                                       name=OutlookCategory.OutlookCategoryNames.FALSE_POSITIVE,
                                       account_outlook_setting=setting)

        # Act
        AccountOutlookSetting.objects.filter(account=self.base_account).delete_categories()

        # Assert
        assert AccountOutlookSetting.objects.filter(account=self.base_account,
                                                    categorize_email=False,
                                                    outlook_categories__isnull=True
                                                    ).count() == 1

    # # Account Model #
    def test_account_create_triggers_account_outlook_setting(self, mock_graphcaller):
        # Arrange
        self.organization.outlook_categorize_email_permission = OutlookCategorizeChoices.ORG_LEVEL
        self.organization.save()
        # Act
        acc = Account.objects.create(username="carol",
                                     first_name="Carol",
                                     last_name="Pilbasian",
                                     organization=self.organization)

        # Assert
        assert acc.outlook_settings.match_category.category_uuid == "a_very_real_category_id"
        assert acc.outlook_settings.false_positive_category.category_uuid == \
            "a_very_real_category_id"

    def test_account_bulk_create_triggers_account_outlook_setting(self, mock_graphcaller):
        # Act
        Account.objects.bulk_create(
            [
                Account(
                    username="carol",
                    first_name="Carol",
                    last_name="Pilbasian",
                    organization=self.organization_org_level

                )
            ]
        )

        # Assert
        assert OutlookCategory.objects.filter(
            account_outlook_setting__account__username="carol",
            account_outlook_setting__categorize_email=True,
            category_uuid="a_very_real_category_id"
        ).count() == 2

    def test_account_delete_removes_outlook_setting(self):
        # Arrange
        # Create an AccountOutlookSetting object
        setting = AccountOutlookSetting.objects.create(account=self.base_account)
        OutlookCategory.objects.create(category_uuid="123",
                                       name=OutlookCategory.OutlookCategoryNames.MATCH,
                                       account_outlook_setting=setting)
        OutlookCategory.objects.create(category_uuid="1234",
                                       name=OutlookCategory.OutlookCategoryNames.FALSE_POSITIVE,
                                       account_outlook_setting=setting)

        # Act
        self.base_account.delete()

        # Assert
        assert AccountOutlookSetting.objects.count() == 0

    # Organization Model #
    def test_organization_bulk_update_org_level_triggers_account_outlook_setting(self,
                                                                                 mock_graphcaller):
        # Arrange
        self.organization.outlook_categorize_email_permission = OutlookCategorizeChoices.ORG_LEVEL

        # Act
        Organization.objects.bulk_update(
            [self.organization],
            ["outlook_categorize_email_permission"])

        # Assert
        assert OutlookCategory.objects.filter(
            account_outlook_setting__account__organization=self.organization,
            category_uuid="a_very_real_category_id").count() == 2

    def test_organization_bulk_update_ind_level_dont_trigger_account_outlook_setting(
            self, mock_graphcaller):
        # Arrange
        self.organization.outlook_categorize_email_permission = (
            OutlookCategorizeChoices.INDIVIDUAL_LEVEL)
        # Act
        Organization.objects.bulk_update(
            [self.organization],
            ["outlook_categorize_email_permission"])

        # Assert
        assert AccountOutlookSetting.objects.filter(
            account__organization=self.organization).count() == 0

    def test_organization_bulk_update_none_dont_trigger_account_outlook_setting(self,
                                                                                mock_graphcaller):
        # Arrange
        self.organization.outlook_categorize_email_permission = OutlookCategorizeChoices.NONE

        # Act
        Organization.objects.bulk_update(
            [self.organization],
            ["outlook_categorize_email_permission"])

        # Assert
        assert AccountOutlookSetting.objects.filter(
            account__organization=self.organization).count() == 0

    def test_organization_bulk_update_none_removes_existing(self,
                                                            mock_graphcaller):
        # Arrange
        Account.objects.bulk_create(
            [
                Account(
                    username="todd",
                    first_name="Todd",
                    last_name="Rodriguez",
                    organization=self.organization_org_level

                )
            ]
        )

        # Act
        assert AccountOutlookSetting.objects.filter(
            account__organization=self.organization_org_level,
            categorize_email=True).count() == 1

        self.organization_org_level.\
            outlook_categorize_email_permission = OutlookCategorizeChoices.NONE

        Organization.objects.bulk_update(
            [self.organization_org_level],
            ["outlook_categorize_email_permission"])

        # Assert
        assert AccountOutlookSetting.objects.filter(
            account__organization=self.organization_org_level,
            categorize_email=True).count() == 0
