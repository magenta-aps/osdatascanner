import pytest
from functools import partial

from django.core.management import call_command as _call_command


call_command = partial(_call_command, "print_objects")


@pytest.mark.django_db
class TestDiagnosticsCommand:
    @pytest.mark.parametrize('args,in_stdout,not_in_stdout', [
        (["Organization", "--filter", "name__contains=g2"],
         ["name: test_org2"],
         # If we're only printing test_org2, then we shouldn't be printing
         # properties from test_org
         ["Mr. DPO-man"]),
        (["Organization", "--filter", "name=test_org", "--field", "dpo_value"],
         ["- dpo_value: dpo@testorg.com"],
         # We've only selected dpo_value, so this dpo_name value shouldn't be
         # printed
         ["Mr. DPO-man"]),
        (["Organization", "--exclude", "name__contains=g2"],
         ["Mr. DPO-man"], []),
        (["Organization", "--no-results"],
         ["2 row(s)"],
         # No actual properties should be printed out when using --no-results
         ["name: test_org2"]),
        (["GraphGrant"],
         ["12345678-1234-1234-1234-123456789012"],
         # Values that look secret shouldn't be printed
         ["very secret secret"]),
    ])
    def test_partial_diagnostics(
            self, args, in_stdout, not_in_stdout,
            *,
            capfd, msgraph_grant, test_org, test_org2):
        # Arrange
        pass

        # Act
        call_command(*args)

        # Assert
        stdout, stderr = capfd.readouterr()

        for string in in_stdout:
            assert string in stdout
        for string in not_in_stdout:
            assert string not in stderr
