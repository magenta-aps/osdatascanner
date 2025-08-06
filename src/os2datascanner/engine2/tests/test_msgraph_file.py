from ..model.msgraph.files import MSGraphDriveHandle, MSGraphFilesSource


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
        # And object like this has everything required to exist, is present in the wild,
        # and as so, should *always* be convertable.
        obj = {'type': 'msgraph-files', 'userlist': None, 'client_id': None,
               'tenant_id': 'aaa12345-12aa-1234-1a23-abcdefghijkl', 'site_drives': True,
               'user_drives': True, 'client_secret': None}

        assert isinstance(MSGraphFilesSource.from_json_object(obj), MSGraphFilesSource)
