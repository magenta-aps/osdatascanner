from requests import Session

from unittest.mock import MagicMock, patch

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
        },
        timeout=120,
    )
    assert r == {"foo": "bar"}


@patch(
    "os2datascanner.projects.admin.import_services.utils.post_import_cleanup"
)
@patch(
    "os2datascanner.projects.admin.organizations.os2mo_import_actions.perform_os2mo_import"
)
@patch.object(Session, "post")
@patch(
    "os2datascanner.projects.admin.import_services.models.os2mo_import_job.make_token",
    return_value="fake_token"
)
def test_run(
    mock_make_token: MagicMock,
    mock_post: MagicMock,
    mock_perform_os2mo_import: MagicMock,
    mock_post_import_cleanup: MagicMock,
):
    # Arrange
    mo_response1 = MagicMock()
    mo_response1.json.return_value = GQL_RESPONSE

    mo_response2 = MagicMock()
    mo_response2.json.return_value = GQL_RESPONSE  # Ok to reuse response

    mo_response3 = MagicMock()
    mo_response3.json.return_value = {
        "data": {
            "org_units": {
                "page_info": {
                    "next_cursor": None
                },
                "objects": []
            }
        },
    }

    mock_post.side_effect = [mo_response1, mo_response2, mo_response3]

    class TestableOS2moImportJob(OS2moImportJob):
        organization = None

        def save(
            self, force_insert=False, force_update=False, using=None, update_fields=None
        ):
            pass

    os2mo_import_job = TestableOS2moImportJob()

    # Act
    os2mo_import_job.run()

    # Assert
    mock_perform_os2mo_import.assert_called_once()
    assert mock_perform_os2mo_import.call_args_list[0].args[0] == [
        {"some": "mo unit 1"},
        {"some": "mo unit 2"},
        {"some": "mo unit 1"},  # Same due to reuse in arrange step above
        {"some": "mo unit 2"},  # Same due to reuse in arrange step above
    ]
    mock_post_import_cleanup.assert_called_once()
