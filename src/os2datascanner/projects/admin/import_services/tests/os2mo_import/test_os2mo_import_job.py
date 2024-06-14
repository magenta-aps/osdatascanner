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
