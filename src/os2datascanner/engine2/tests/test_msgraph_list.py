from os2datascanner.engine2.model.core.utilities import SourceManager
import pytest
from os2datascanner.engine2.model.msgraph.lists import MSGraphListsSource


# Fixture to set up the source instance
@pytest.fixture
def msgraph_lists_source():
    return MSGraphListsSource(
        client_id="test-client-id",
        tenant_id="test-tenant-id",
        client_secret="test-client-secret"
    )


class TestMSGraphListsSource:
    def test_handles_filter_logic(self, msgraph_lists_source, mock_graphcaller):
        sm = SourceManager()
        results = list(msgraph_lists_source.handles(sm))

        for result in results:
            print(result.__dict__)

        assert len(results) == 3

        found_lists = [handle.relative_path for handle in results]

        assert "list1" in found_lists
        assert "list4" in found_lists
        assert "list5" in found_lists

        assert "list2" not in found_lists
        assert "list3" not in found_lists
