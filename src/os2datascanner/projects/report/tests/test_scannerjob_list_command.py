import pytest
import re

from django.core.management import call_command

from .test_utilities import create_reports_for


@pytest.mark.django_db
class TestScannerjobListCommand:

    @pytest.mark.parametrize('scannerjobs', [
        ((51, "Super cool job!"), (52, "Another job"), (53, "A third job")),
        ((51, "Super cool job!"), (52, "Another job"), (53, "A third job"), (54, "A fourth job")),
        ((51, "You had one job"),)
    ])
    def test_scannerjob_list_print(self, capfd, egon_email_alias, scannerjobs):
        # Arrange
        for pk, name in scannerjobs:
            create_reports_for(egon_email_alias, num=10, scanner_job_pk=pk, scanner_job_name=name)

        expected = sorted([f"{name} (PK: {pk})" for pk, name in scannerjobs])

        # Act
        call_command("scannerjob_list")

        out = capfd.readouterr()[0]

        # Assert
        regex = r'(.+ \(PK: \d+\))'

        result = sorted(re.findall(regex, out))

        assert result == expected
