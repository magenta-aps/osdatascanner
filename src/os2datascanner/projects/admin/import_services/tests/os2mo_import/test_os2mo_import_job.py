from unittest.mock import MagicMock

from django.conf import settings
from requests import HTTPError

from os2datascanner.projects.admin.import_services.models.os2mo_import_job import OS2moImportJob

GQL_RESPONSE = {
    "data": {
        "org_units": {
            "page_info": {
                "next_cursor": "some_cursor"
            },
            "objects": [
                {
                    "some": "mo unit 1",
                },
                {
                    "some": "mo unit 2",
                }
            ]
        }
    },
}


def test__get_next_cursor():
    # Act + Assert
    assert OS2moImportJob._get_next_cursor(GQL_RESPONSE) == "some_cursor"


def test__get_org_unit_data():
    assert OS2moImportJob._get_org_unit_data(GQL_RESPONSE) == [
        {
            "some": "mo unit 1",
        },
        {
            "some": "mo unit 2",
        }
    ]


def test__retry_post_query():
    # Arrange
    mo_response = MagicMock()
    mo_response.json.return_value = {"foo": "bar"}

    mock_session = MagicMock()
    mock_session.post.side_effect = [HTTPError(), mo_response]

    # Act
    r = OS2moImportJob._retry_post_query(
        mock_session,
        "fake_token",
        "https://os2mo.magenta.dk/graphql",
        next_cursor="some_cursor",
    )

    # Assert
    assert mock_session.post.call_count == 2
    mock_session.post.assert_called_with(
        "https://os2mo.magenta.dk/graphql",
        json={
            "query": OS2moImportJob.QueryOrgUnitsManagersEmployees,
            "variables": {
                "cursor": "some_cursor",
                "limit": settings.OS2MO_PAGE_SIZE,
                "email_type": settings.OS2MO_EMAIL_ADDRESS_TYPE,
            }
        },
        headers={
            "content-type": "application/json; charset=UTF-8",
            "authorization": "Bearer fake_token"
        }
    )
    assert r == {"foo": "bar"}
