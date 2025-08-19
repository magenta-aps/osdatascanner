import pytest
from django.contrib.auth.models import Permission
from django.urls import reverse

from os2datascanner.projects.grants.models import GraphGrant, SMBGrant, EWSGrant, GoogleApiGrant


@pytest.mark.django_db
class TestGrantListViewGetQueryset:
    @pytest.mark.parametrize(
        "perms,expected_types",
        [
            ([], None),  # no perms
            (["view_graphgrant"], {GraphGrant}),
            (["view_graphgrant", "view_smbgrant"], {GraphGrant, SMBGrant}),
            (
                [
                    "view_graphgrant",
                    "view_smbgrant",
                    "view_ewsgrant",
                    "view_googleapigrant",
                ],
                {GraphGrant, SMBGrant, EWSGrant, GoogleApiGrant},
            ),
        ],
    )
    def test_queryset_permissions(self, client, user, test_org,
                                  exchange_grant, smb_grant, google_api_grant,
                                  msgraph_grant, perms, expected_types):
        """Call GrantListView via URL to test queryset permissions."""

        # Arrange: Assign permissions if any
        if perms:
            user.user_permissions.add(*self._grant_perms(*perms))
        client.force_login(user)

        url = reverse("grant-list")

        # Act
        if expected_types is None:
            # Expect forbidden access
            response = client.get(url)
            assert response.status_code in (403, 302)  # Permission denied or redirect
            return

        response = client.get(url)

        # Assert

        assert response.status_code == 200

        # Get the queryset from the context
        qs = response.context["object_list"]
        orgs = list(qs)
        assert orgs == [test_org]

        returned_types = {type(g) for g in orgs[0].grants}
        assert returned_types == expected_types

    @staticmethod
    def _grant_perms(*full_perms):
        return [Permission.objects.get(codename=perm) for perm in full_perms]
