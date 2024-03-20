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
