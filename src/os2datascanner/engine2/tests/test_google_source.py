import pytest
from unittest.mock import Mock, patch

from os2datascanner.engine2.model.utilities.utilities import GoogleSource

from google.oauth2 import service_account  # noqa mock
from googleapiclient.discovery import build, Resource  # noqa mock


class TestGoogleSource:

    @pytest.fixture
    def mock_google_api_grant(self):
        return {
            "type": "service_account",
            "project_id": "test_project",
            "private_key_id": "fake_key_id",
            "private_key": "-----BEGIN PRIVATE KEY-----\nFAKE_KEY\n-----END PRIVATE KEY-----",
            "client_email": "test@testing.iam.gserviceaccount.com",
            "client_id": "test_client",
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
        }

    @pytest.fixture
    def concrete_google_source_class(self):

        class ConcreteGoogleSource(GoogleSource):
            def handles(self, handle):
                return True

            @property
            def type_label(self):
                return "test_google_source"

        return ConcreteGoogleSource

    @pytest.fixture
    def google_source(self, mock_google_api_grant, concrete_google_source_class):
        return concrete_google_source_class(
            google_api_grant=mock_google_api_grant,
            user_email="testuser1@testing.com",
            scope="drive"
        )

    def test_init(self, mock_google_api_grant, concrete_google_source_class):
        source = concrete_google_source_class(
            google_api_grant=mock_google_api_grant,
            user_email="testuser2@testing.com",
            scope="gmail"
        )

        assert source._google_api_grant == mock_google_api_grant
        assert source._user_email == "testuser2@testing.com"
        assert source.scope == "gmail"

    def test_version_drive(self, google_source):
        assert google_source.version == "v3"

    def test_version_gmail(self, mock_google_api_grant, concrete_google_source_class):
        source = concrete_google_source_class(
            google_api_grant=mock_google_api_grant,
            user_email="testuser3@testing.com",
            scope="gmail"
        )
        assert source.version == "v1"

    def test_version_unknown_scope(self, mock_google_api_grant, concrete_google_source_class):
        source = concrete_google_source_class(
            google_api_grant=mock_google_api_grant,
            user_email="testuser4@testing.com",
            scope="unknown_service"
        )
        with pytest.raises(KeyError):
            assert source.version

    def test_paginated_get_single_page(self, google_source):
        mock_service = Mock()
        mock_list = Mock()
        mock_service.list.return_value = mock_list
        mock_list.execute.return_value = {
            "files": [
                        {"id": "1", "name": "Test File 1"},
                        {"id": "2", "name": "Test File 2"}
                     ],
            "nextPageToken": None
        }

        results = list(google_source.paginated_get(mock_service, "files", q="mimeType=text/plain"))

        assert len(results) == 2
        assert results[0] == {"id": "1", "name": "Test File 1"}
        assert results[1] == {"id": "2", "name": "Test File 2"}
        mock_service.list.assert_called_once_with(q="mimeType=text/plain")

    def test_paginated_get_multiple_pages(self, google_source):
        mock_service = Mock()

        mock_list_1 = Mock()
        mock_list_1.execute.return_value = {
            "files": [{"id": "1", "name": "Test File 1"}],
            "nextPageToken": "page2"
        }

        mock_list_2 = Mock()
        mock_list_2.execute.return_value = {
            "files": [{"id": "2", "name": "Test File 2"}],
            "nextPageToken": None
        }

        mock_service.list.side_effect = [mock_list_1, mock_list_2]

        results = list(google_source.paginated_get(mock_service, "files", q="test"))

        assert len(results) == 2
        assert results[0] == {"id": "1", "name": "Test File 1"}
        assert results[1] == {"id": "2", "name": "Test File 2"}
        assert mock_service.list.call_count == 2

        second_call_kwargs = mock_service.list.call_args_list[1][1]
        assert second_call_kwargs["pageToken"] == "page2"

    def test_paginated_get_empty_collection(self, google_source):
        mock_service = Mock()
        mock_list = Mock()
        mock_service.list.return_value = mock_list
        mock_list.execute.return_value = {
            "nextPageToken": None
        }

        results = list(google_source.paginated_get(mock_service, "files"))

        assert len(results) == 0

    def test_paginated_get_with_kwargs(self, google_source):
        mock_service = Mock()
        mock_list = Mock()
        mock_service.list.return_value = mock_list
        mock_list.execute.return_value = {
            "files": [{"id": "1"}],
            "nextPageToken": None
        }

        list(google_source.paginated_get(
            mock_service,
            "files",
            q="test query",
            pageSize=100,
            fields="id,name"
        ))

        mock_service.list.assert_called_once_with(
            q="test query",
            pageSize=100,
            fields="id,name"
        )

    def test_censor(self, google_source, concrete_google_source_class):
        censored = google_source.censor()

        assert isinstance(censored, concrete_google_source_class)
        assert censored._google_api_grant is None
        assert censored._user_email == "testuser1@testing.com"
        assert censored.scope == "drive"

    @patch('googleapiclient.discovery.build')
    @patch('google.oauth2.service_account.Credentials.from_service_account_info')
    def test_generate_state(self, mock_credentials, mock_build, google_source,
                            mock_google_api_grant):
        mock_creds = Mock()
        mock_creds_with_subject = Mock()
        mock_creds.with_subject.return_value = mock_creds_with_subject
        mock_credentials.return_value = mock_creds

        mock_service = Mock()
        mock_build.return_value = mock_service

        gen = google_source._generate_state(None)
        service = next(gen)

        mock_credentials.assert_called_once_with(
            mock_google_api_grant,
            scopes=['https://www.googleapis.com/auth/drive.readonly']
        )
        mock_creds.with_subject.assert_called_once_with("testuser1@testing.com")

        assert isinstance(service, Resource)
