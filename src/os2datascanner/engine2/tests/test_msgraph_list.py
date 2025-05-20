import pytest
from os2datascanner.engine2.model.msgraph.lists import MSGraphListsSource


class MockConnection:
    def __init__(self, responses):
        self.responses = responses
        self.call_count = 0
        self.calls = []
    
    def paginated_get(self, url):
        self.calls.append(url)
        response = self.responses[self.call_count]
        self.call_count += 1
        return response


class MockSessionManager:
    def __init__(self, connection):
        self.connection = connection
        self.open_calls = []
    
    def open(self, source):
        self.open_calls.append(source)
        return self.connection


@contextmanager
def mock_warn_on_httperror(message):
    yield None


# Fixture to set up the source instance
@pytest.fixture
def msgraph_lists_source():
    return MSGraphListsSource(
        client_id="test-client-id",
        tenant_id="test-tenant-id",
        client_secret="test-client-secret"
    )


# Fixture to set up test data
@pytest.fixture
def test_data():
    # Sites data
    sites = [
        {"id": "domain,site1"},
        {"id": "domain,site2"}
    ]
    
    # Lists for site1
    site1_lists = [
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
            "webUrl": "https://example.com/sites/site1/lists/_catalog/content"
        }
    ]
    
    # Lists for site2
    site2_lists = [
        {
            "id": "list4",
            "name": "Another Regular List",
            "list": {"template": "genericList"},
            "webUrl": "https://example.com/sites/site2/lists/regular"
        },
        {
            "id": "list5",
            "name": "Another Catalog",
            "list": {"template": "taskList"},
            "webUrl": "https://example.com/sites/site2/lists/web_catalog"
        }
    ]
    
    return {
        "sites": sites,
        "site1_lists": site1_lists,
        "site2_lists": site2_lists
    }

@pytest.fixture
def mock_sm(test_data):
    mock_conn = MockConnection([
        test_data["sites"],
        test_data["site1_lists"],
        test_data["site2_lists"]
    ])
    return MockSessionManager(mock_conn)


def test_handles_filter_logic(msgraph_lists_source, mock_sm):
    results = list(msgraph_lists_source.handles(mock_sm))
    
    assert len(results) == 2 
    
    found_lists = [handle.relative_path for handle in results]
    
    assert "list1" in found_lists
    assert "list4" in found_lists
    
    assert "list2" not in found_lists
    assert "list3" not in found_lists
    assert "list5" not in found_lists