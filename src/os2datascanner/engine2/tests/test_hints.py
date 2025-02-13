import pytest

from os2datascanner.engine2.model.smbc import SMBCSource, SMBCHandle


@pytest.fixture
def hint_dict():
    return {
        "biscuits": "tasty",
        "pet_count": {
            "dog": 4,
            "cat": 3.14159,  # one very round cat(?)
            "gerbil": 3,
        }
    }


@pytest.fixture
def source():
    return SMBCSource("//SERVER/Resource", "username", "topsecret", "WORKGROUP8")


@pytest.fixture
def handle(source, hint_dict):
    return SMBCHandle(source, "~ocument.docx", hints=hint_dict)


class TestHint:
    def test_hint_serialisation(self, handle, hint_dict):
        """Hints survive serialisation and deserialisation."""
        rtd_handle = SMBCHandle.from_json_object(handle.to_json_object())

        for k in hint_dict.keys():
            hint = handle.hint(k)
            assert hint is not None
            assert hint == rtd_handle.hint(k)

    def test_hint_deletion(self, handle, hint_dict):
        """Hints associated with an object can be deleted."""
        handle.clear_hints()

        for k in hint_dict.keys():
            assert handle.hint(k) is None
