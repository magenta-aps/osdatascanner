import pytest
from io import BytesIO
from requests.models import Response
from os2datascanner.engine2.model.core.utilities import SourceManager


@pytest.fixture
def mock_graphcaller(monkeypatch):
    def mock_open(*args, **kwargs):
        return MockGraphCaller()

    # Mock the 'open' method of the SourceManager object
    monkeypatch.setattr(SourceManager, "open", mock_open)


class MockGraphCaller:
    def get(self, *args, **kwargs):
        # Used in test_msgraph_mail.py
        res = Response()
        res.code = 200
        res.raw = BytesIO(b'{ "id" : "a_very_real_folder_id" }')
        return res

    def paginated_get(self, url, *args, **kwargs):
        match url:
            case "sites/getAllSites?$filter=isPersonalSite ne true":
                return [
                    {"id": "domain,site1"},
                    {"id": "domain,site2"}
                ]
            case "sites/site1/lists":
                return [
                    {
                        "id": "list1",
                        "name": "Regular List",
                        "list": {"template": "genericList"},
                        "webUrl": "https://example.com/sites/site1/lists/regular"
                    },
                    {
                        "id": "list2",
                        "name": "Document Library",
                        "list": {"template": "documentLibrary"},
                        "webUrl": "https://example.com/sites/site1/lists/docs"
                    },
                    {
                        "id": "list3",
                        "name": "Catalog List",
                        "list": {"template": "genericList"},
                        "webUrl": "https://example.com/sites/site1/lists/_catalogs/content"
                    }
                ]
            case "sites/site2/lists":
                return [
                    {
                        "id": "list4",
                        "name": "Another Regular List",
                        "list": {"template": "genericList"},
                        "webUrl": "https://example.com/sites/site2/lists/regular"
                    },
                    {
                        "id": "list5",
                        "name": "Sneaky Catalog",
                        "list": {"template": "taskList"},
                        "webUrl": "https://example.com/sites/site2/lists/web_catalog"
                    }
                ]

        return None
