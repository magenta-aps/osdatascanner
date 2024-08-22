import pytest
import re

from django.core.management import call_command
from django.contrib.auth import get_user_model


@pytest.fixture
def existing_user():
    user = get_user_model().objects.create_superuser("dev", "dev")
    return user


@pytest.fixture
def debug_setting_on(temp_settings):
    temp_settings.DEBUG = True


@pytest.mark.django_db
class TestQuickstartDevCommand:

    def test_debug_off(self, temp_settings, existing_user):
        temp_settings.DEBUG = False

        with pytest.raises(SystemExit) as pytest_wrapped_e:
            call_command("quickstart_dev")
        assert pytest_wrapped_e.value.code == 1

    def test_no_user(self, debug_setting_on, capfd):
        """The command should fail if there is no user with username 'dev'."""

        call_command("quickstart_dev")

        out = capfd.readouterr()[0]

        stdout_match = re.search(r"User does not exist! Did you run this "
                                 r"command in the admin module\?", out)

        assert stdout_match

    def test_user_is_staff(self, debug_setting_on, existing_user):
        """The command should find the user with username 'dev', and set the
        'is_staff'-flag to True."""

        call_command("quickstart_dev")
        user = get_user_model().objects.get(username="dev")
        assert user.is_staff

    def test_user_password(self, debug_setting_on, existing_user):
        """The command should find the user with username 'dev', and set the
        password to 'dev'."""

        call_command("quickstart_dev")
        user = get_user_model().objects.get(username="dev")
        assert user.check_password("dev")
