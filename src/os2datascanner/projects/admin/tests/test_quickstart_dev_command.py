import pytest

from django.core.management import call_command
from django.contrib.auth import get_user_model

from ..core.models.client import Client
from ..organizations.models.organization import Organization
from ..organizations.models.aliases import Alias, AliasType
from ..adminapp.models.rules import CustomRule
from ..adminapp.models.authentication import Authentication
from ..adminapp.models.scannerjobs.filescanner import FileScanner
from ..adminapp.models.scannerjobs.webscanner import WebScanner


@pytest.fixture
def debug_setting_on(temp_settings):
    temp_settings.DEBUG = True
    temp_settings.PRODUCTION = False


@pytest.mark.django_db
class TestQuickstartDevCommand:

    def test_debug_off(self, temp_settings):
        temp_settings.DEBUG = False
        temp_settings.PRODUCTION = False

        with pytest.raises(SystemExit) as pytest_wrapped_e:
            call_command("quickstart_dev")
        assert pytest_wrapped_e.value.code == 1

    def test_production_on(self, temp_settings):
        temp_settings.DEBUG = True
        temp_settings.PRODUCTION = True

        with pytest.raises(SystemExit) as pytest_wrapped_e:
            call_command("quickstart_dev")
        assert pytest_wrapped_e.value.code == 1

    @pytest.mark.parametrize('model,expected_fields',
                             [(Client,
                               {'name': 'Development Client'}),
                                 (Organization,
                                  {'name': 'OSdatascanner'}),
                                 (CustomRule,
                                  {'name': 'CPR regel',
                                   'description': 'Denne regel finder alle gyldige CPR numre.'}),
                                 (get_user_model(),
                                  {'username': 'dev',
                                     'email': 'dev@example.org',
                                     'is_superuser': True,
                                     'is_staff': True}),
                                 (Alias,
                                  {'_alias_type': AliasType.REMEDIATOR,
                                   '_value': '0'}),
                                 (FileScanner,
                                  {'name': 'Lille Samba',
                                   'unc': '//samba/e2test',
                                   'do_ocr': True,
                                   'validation_status': True,
                                   'do_last_modified_check': False}),
                                 (Authentication,
                                  {'username': 'os2'}),
                                 (WebScanner,
                                  {'name': 'Local nginx',
                                   'url': 'http://nginx/',
                                   'validation_status': True,
                                   'do_last_modified_check': False,
                                   'download_sitemap': False}),
                              ])
    def test_created_object_fields(self, debug_setting_on, model, expected_fields):
        call_command("quickstart_dev")

        obj = model.objects.first()

        for field, value in expected_fields.items():
            assert getattr(obj, field) == value

    def test_created_autentication_password(self, debug_setting_on):
        call_command("quickstart_dev")

        auth = Authentication.objects.first()

        assert auth.get_password() == "swordfish"

    def test_created_user_password(self, debug_setting_on):
        call_command("quickstart_dev")

        user = get_user_model().objects.first()

        assert user.check_password("dev")

    def test_org_connections(self, debug_setting_on):
        call_command("quickstart_dev")

        org = Organization.objects.first()

        assert org.client.name == 'Development Client'
        assert org.user_accounts.first().username == 'dev'
        assert org.system_rules.first().name == 'CPR regel'
        assert org.scannerjob.order_by('name').first().name == 'Lille Samba'
        assert org.scannerjob.order_by('name').last().name == 'Local nginx'
