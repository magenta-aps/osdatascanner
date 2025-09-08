from os2datascanner.engine2.model.core.utilities import SourceManager
import pytest
from os2datascanner.engine2.model.msgraph.lists import MSGraphListsSource, MSGraphListItemResource
import csv
from io import StringIO


@pytest.fixture
def csv_parser():

    def parse_csv_bytes(csv_bytes):
        csv_string = csv_bytes.decode('utf-8')
        reader = csv.DictReader(StringIO(csv_string))
        return next(reader)

    return parse_csv_bytes

# Fixture to set up the source instance


@pytest.fixture
def msgraph_lists_source():
    return MSGraphListsSource(
        client_id="test-client-id",
        tenant_id="test-tenant-id",
        client_secret="test-client-secret"
    )


@pytest.fixture
def msgraph_lists_item_resource():
    return MSGraphListItemResource("sm", "handle")


@pytest.fixture
def json_input():
    return {
        "@odata.etag": "\"etag,16\"",
        "Title": "Darth Plagueis",
        "LongText": "Did you ever hear the tragedy of Darth Plagueis The Wise?",
        "Nested": {
            "IThoughtNot": {
                "ItIsNotAStory": "The jedi would tell you"
            },
            "Its": "A sith story"
        },
        "EmptyField": "",
        "bool": True,
        'mixed': ['text', 42, True, None],
        'empty_list': [],
        "id": "1",
        "ContentType": "Element",
        "Modified": "2025-06-22T21:19:49Z",
        "Created": "2025-04-24T12:36:42Z",
        "AuthorLookupId": "15",
        "EditorLookupId": "15",
        "_UIVersionString": "15.0",
        "Attachments": True,
        "Edit": "",
        "LinkTitleNoMenu": "Darth Plagueis the Wise.",
        "LinkTitle": "Darth Plagueis the Wise.",
        "ItemChildCount": "0",
        "FolderChildCount": "0",
        "_ComplianceFlags": "",
        "_ComplianceTag": "",
        "_ComplianceTagWrittenTime": "",
        "_ComplianceTagUserId": ""
    }


class TestMSGraphListsSource:
    def test_handles_filter_logic(self, msgraph_lists_source, mock_graphcaller):
        sm = SourceManager()
        results = list(msgraph_lists_source.handles(sm))

        assert len(results) == 3

        found_lists = [handle.relative_path for handle in results]

        assert "list1" in found_lists
        assert "list4" in found_lists
        assert "list5" in found_lists

        assert "list2" not in found_lists
        assert "list3" not in found_lists


class TestMSGraphListItemResource:
    def test_excludes_columns(self, msgraph_lists_item_resource, json_input, csv_parser):
        exclude_columns = [
            '@odata.etag', 'id', 'ContentType', 'Modified', 'Created',
            'AuthorLookupId', 'EditorLookupId', '_UIVersionString',
            'Attachments', 'Edit', 'LinkTitleNoMenu', 'LinkTitle',
            'ItemChildCount', 'FolderChildCount', '_ComplianceFlags',
            '_ComplianceTag', '_ComplianceTagWrittenTime',
            '_ComplianceTagUserId', 'AppEditorLookupId'
        ]

        result = msgraph_lists_item_resource.json_to_csv_bytes(json_input)
        parsed = csv_parser(result)

        for key in exclude_columns:
            assert key not in parsed

        assert parsed['Title'] == 'Darth Plagueis'
        assert parsed['LongText'] == 'Did you ever hear the tragedy of Darth Plagueis The Wise?'

    def test_flattens(self, msgraph_lists_item_resource, json_input, csv_parser):
        result = msgraph_lists_item_resource.json_to_csv_bytes(json_input)
        parsed = csv_parser(result)

        assert parsed['Nested.Its'] == 'A sith story'
        assert parsed['Nested.IThoughtNot.ItIsNotAStory'] == 'The jedi would tell you'

    def test_converts_lists(self, msgraph_lists_item_resource, json_input, csv_parser):
        result = msgraph_lists_item_resource.json_to_csv_bytes(json_input)
        parsed = csv_parser(result)

        assert parsed['mixed'] == 'text; 42; True; None'
        assert parsed['empty_list'] == ''

    def test_converts_booleans_to_strings(self,
                                          msgraph_lists_item_resource,
                                          json_input,
                                          csv_parser):
        result = msgraph_lists_item_resource.json_to_csv_bytes(json_input)
        parsed = csv_parser(result)

        assert parsed['bool'] == 'True'

    def test_converts_none_values_to_empty_strings(self, msgraph_lists_item_resource,
                                                   json_input,
                                                   csv_parser):
        result = msgraph_lists_item_resource.json_to_csv_bytes(json_input)
        parsed = csv_parser(result)

        assert parsed['EmptyField'] == ''
