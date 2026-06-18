from unittest.mock import MagicMock

import pytest

from os2datascanner.projects.admin.core import forms as core_forms
from os2datascanner.projects.admin.core.forms import ClientAdminForm
from os2datascanner.projects.admin.core.models.client import Client, ImportSource
from os2datascanner.projects.admin.import_services.models.import_service import ImportService
from os2datascanner.projects.admin.organizations.models import Organization


_VALID_CLIENT_FORM_DATA = {
    "contact_email": "test@example.com",
    "contact_phone": "12345678",
    "explorer_delta_queue": "os2ds_scan_specs",
    "explorer_full_queue": "os2ds_scan_specs",
    "conversion_delta_queue": "os2ds_conversions",
    "conversion_full_queue": "os2ds_conversions",
    "activated_scan_types": [],
}


@pytest.mark.django_db
def test_changing_import_source_clears_import_services(monkeypatch):
    client = Client.objects.create(name="switch_client", import_source=ImportSource.LDAP)
    cleared = MagicMock()
    monkeypatch.setattr(core_forms, "clear_import_services", cleared)

    form = ClientAdminForm(
        data=_VALID_CLIENT_FORM_DATA | {
            "name": client.name,
            "import_source": ImportSource.MS_GRAPH},
        instance=client,
         )
    assert form.is_valid(), form.errors
    form.save()

    cleared.assert_called_once_with(client)


@pytest.mark.django_db
def test_unchanged_import_source_keeps_import_services(monkeypatch):
    client = Client.objects.create(name="stable_client", import_source=ImportSource.LDAP)
    cleared = MagicMock()
    monkeypatch.setattr(core_forms, "clear_import_services", cleared)

    form = ClientAdminForm(
        data=_VALID_CLIENT_FORM_DATA | {"name": client.name, "import_source": ImportSource.LDAP},
        instance=client,
    )
    assert form.is_valid(), form.errors
    form.save()

    cleared.assert_not_called()


@pytest.mark.django_db
def test_changing_import_source_deletes_import_service_rows():
    client = Client.objects.create(name="real_client", import_source=ImportSource.LDAP)
    org = Organization.objects.create(name="real_org", client=client)
    ImportService.objects.create(organization=org)

    form = ClientAdminForm(
        data=_VALID_CLIENT_FORM_DATA | {
            "name": client.name,
            "import_source": ImportSource.MS_GRAPH},
        instance=client,
         )
    assert form.is_valid(), form.errors
    form.save()

    assert not ImportService.objects.filter(organization=org).exists()
