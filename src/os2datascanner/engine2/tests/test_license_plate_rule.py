import pytest
from os2datascanner.engine2.rules.license_plate import DanishLicensePlateRule


@pytest.mark.parametrize("test_input, expected", [("BA 21 456", ["BA 21 456"]),
                                                  ("ba 21 456", ["ba 21 456"]),
                                                  ("AZ69420", ["AZ69420"]),
                                                  ("az69420", ["az69420"]),
                                                  ("AZ 69420", ["AZ 69420"]),
                                                  ("az 69420", ["az 69420"]),
                                                  ("AZ69 420", ["AZ69 420"]),
                                                  ("az69 420", ["az69 420"]),
                                                  ("B 12 456", []),
                                                  ("AB 1 123", []), ("AB 12 3", []),
                                                  ("123 12 AB", []), ("12 123 AB", []),
                                                  ("12 AB 123", []), ("AB 123 12", []),
                                                  ("ABBA 12 345", []), ("BA 12 3456789", []),
                                                  ("az-12-123", []), ("AZ-12-123", []),
                                                  ("AB 23 345.", ["AB 23 345"]),
                                                  ("Ab12345", ["Ab12345"]),
                                                  (":AB 12 345", ["AB 12 345"]),
                                                  (".ba 12 182,", ["ba 12 182"])])
def test_license_plate(test_input: str, expected: list[str]):
    rule = DanishLicensePlateRule()
    results = [match_obj["match"] for match_obj in rule.match(test_input)]
    assert results == expected
