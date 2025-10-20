from ..model.msgraph.files import MSGraphDriveHandle, MSGraphFilesSource, MSGraphDriveSource
from datetime import datetime, timezone


class TestMSGraphDriveHandle:
    def test_equaliy_properties(self):
        # Arrange
        fake_source = MSGraphFilesSource(
                                    "Not a real client ID value",
                                    "Not a real tenant ID value",
                                    "Not a very secret client secret")

        handle1 = MSGraphDriveHandle(fake_source,
                                     "123identifier",
                                     "Bilag og Udgifter",
                                     "Lars",
                                     user_account="Statsminister-Lars")

        handle2 = MSGraphDriveHandle(fake_source,
                                     "123identifier",
                                     "Fadbamser",
                                     "Lars",
                                     user_account="Privat-Lars")

        # Though they might seem it, Privat-Lars and Statsminister-Lars are
        # not the same.
        # Act
        the_same = handle1 == handle2

        # Assert
        assert not the_same

    def test_to_json_object(self):
        # An object like this has everything required to exist, is present in the wild,
        # and as so, should *always* be convertable.
        obj = {'type': 'msgraph-files', 'userlist': None, 'client_id': None,
               'tenant_id': 'aaa12345-12aa-1234-1a23-abcdefghijkl', 'site_drives': True,
               'user_drives': True, 'client_secret': None}

        assert isinstance(MSGraphFilesSource.from_json_object(obj), MSGraphFilesSource)


class TestMSGraphDriveSource:
    def test_last_modified_filer(self):
        fake_source = MSGraphFilesSource(
                                    "Not a real client ID value",
                                    "Not a real tenant ID value",
                                    "Not a very secret client secret")
        fake_handle = MSGraphDriveHandle(fake_source,
                                         "path",
                                         "Folder",
                                         "User",
                                         user_account="Test User"
                                         )

        fake_drive_source = MSGraphDriveSource(fake_handle)
        fake_folder = [{
                          "id": 1,
                          "lastModifiedDateTime": "1996-06-27T12:25:30Z",
                          "name": "testfile1"
                        },
                       {
                            "id": 2,
                            "lastModifiedDateTime": "1997-02-11T12:25:30Z",
                            "name": "Testfile2"
                        }]

        cutoff = datetime(1997, 1, 1, 12, 00, 00, tzinfo=timezone.utc)

        filtered_folder = fake_drive_source.filter_last_modified(fake_folder, cutoff)

        assert len(filtered_folder) == 1
        assert fake_folder != filtered_folder
        assert filtered_folder[0]['id'] == 2
