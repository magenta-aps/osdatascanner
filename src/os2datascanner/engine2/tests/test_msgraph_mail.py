import pytest
from io import BytesIO
from requests.models import Response
from os2datascanner.engine2.model.msgraph.mail import MSGraphMailAccountSource
from os2datascanner.engine2.model.core.utilities import SourceManager


class MockGraphCaller:
    def get(self, *args, **kwargs):
        res = Response()
        res.code = 200
        res.raw = BytesIO(b'{ "id" : "a_very_real_folder_id" }')
        return res


@pytest.fixture
def mock_graphcaller(monkeypatch):
    def mock_open(*args, **kwargs):
        return MockGraphCaller()

    # Mock the 'open' method of the SourceManager object
    monkeypatch.setattr(SourceManager, "open", mock_open)


class TestMSGraphMailAccountSource:
    pn = "osdatascanner@microsoft.cloud"
    ps = 1
    sm = SourceManager()
    # it's a bit wonky to query hardcoded, but that's what we do and it's not what's relevant
    # for this test.
    query = f"users/{pn}/messages?$select=id,subject,webLink,parentFolderId&$top={ps}"

    def test_scan_deleted_and_sync_issues(self):
        # Arrange
        scan_deleted_items = scan_sync_issues = True

        # Act
        query = MSGraphMailAccountSource._append_msgraph_filters(self,
                                                                 self.pn, self.query, self.sm,
                                                                 scan_deleted_items,
                                                                 scan_sync_issues)

        # Assert
        # Shouldn't exclude anything.
        assert query == ("users/osdatascanner@microsoft.cloud/messages?$select=id,subject,webLink,"
                         "parentFolderId&$top=1")

    def test_dont_scan_deleted_or_sync_issues(self, mock_graphcaller):
        # Arrange
        scan_deleted_items = scan_sync_issues = False

        # Act
        query = MSGraphMailAccountSource._append_msgraph_filters(self,
                                                                 self.pn, self.query, self.sm,
                                                                 scan_deleted_items,
                                                                 scan_sync_issues)

        # Assert
        # Should exclude three folders
        assert query == ("users/osdatascanner@microsoft.cloud/messages?$select=id,subject,webLink,"
                         "parentFolderId&$top=1&$filter=parentFolderId "
                         "ne 'a_very_real_folder_id' "
                         "and parentFolderId ne 'a_very_real_folder_id' "
                         "and parentFolderId ne 'a_very_real_folder_id'")

    def test_scan_deleted_but_not_sync_issues(self, mock_graphcaller):
        # Arrange
        scan_deleted_items = True
        scan_sync_issues = False

        # Act
        query = MSGraphMailAccountSource._append_msgraph_filters(self,
                                                                 self.pn, self.query, self.sm,
                                                                 scan_deleted_items,
                                                                 scan_sync_issues)

        # Assert
        # Should exclude two folders
        assert query == ("users/osdatascanner@microsoft.cloud/messages?$select=id,subject,webLink,"
                         "parentFolderId&$top=1&$filter=parentFolderId "
                         "ne 'a_very_real_folder_id' "
                         "and parentFolderId ne 'a_very_real_folder_id'")

    def test_scan_sync_issues_but_not_deleted(self, mock_graphcaller):
        # Arrange
        scan_deleted_items = False
        scan_sync_issues = True

        # Act
        query = MSGraphMailAccountSource._append_msgraph_filters(self,
                                                                 self.pn, self.query, self.sm,
                                                                 scan_deleted_items,
                                                                 scan_sync_issues)

        # Assert
        # Should exclude one folder
        assert query == ("users/osdatascanner@microsoft.cloud/messages?$select=id,subject,webLink,"
                         "parentFolderId&$top=1&$filter=parentFolderId "
                         "ne 'a_very_real_folder_id'")
