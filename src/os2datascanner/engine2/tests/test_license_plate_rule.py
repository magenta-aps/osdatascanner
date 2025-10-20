import pytest
from os2datascanner.engine2.rules.license_plate import LicensePlateRule


@pytest.mark.parametrize("test_input, expected", [("BA 21 456", "BA 21 456"), ("B 12 456", ""),
                                                  ("AB 1 123", ""), ("AB 12 3", ""),
                                                  ("123 12 AB", ""), ("12 123 AB", ""),
                                                  ("12 AB 123", ""), ("AB 123 12", "")])
def test_license_plate(test_input, expected):
    rule = LicensePlateRule()
    results = rule.match(test_input)
    for result in results:
        assert result["match"] == expected
