# Part of the OSdatascanner system, copyright © 2014-2026 Magenta ApS.
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, you can
# obtain one at http://mozilla.org/MPL/2.0/.

from django.db import migrations, models

_LDAP = 1 << 2
_MS_GRAPH = 1 << 3
_OS2MO = 1 << 4
_GOOGLE = 1 << 5


def features_to_import_source(features):
    """Map the legacy `features` bitmask to a single `import_source` value.

    Only the import-service bits matter. ADMIN_API and ORG_STRUCTURE are dropped.
    The legacy admin form guaranteed at most one import bit was ever set.
    """
    if features & _LDAP:
        return "ldap"
    if features & _MS_GRAPH:
        return "msgraph"
    if features & _OS2MO:
        return "os2mo"
    if features & _GOOGLE:
        return "google"
    return "none"


def import_source_to_features(value):
    return {
        "ldap": _LDAP,
        "msgraph": _MS_GRAPH,
        "os2mo": _OS2MO,
        "google": _GOOGLE,
    }.get(value, 0)


def forwards(apps, schema_editor):
    Client = apps.get_model("core", "Client")
    for client in Client.objects.all():
        client.import_source = features_to_import_source(client.features)
        client.save(update_fields=["import_source"])


def backwards(apps, schema_editor):
    Client = apps.get_model("core", "Client")
    for client in Client.objects.all():
        client.features = import_source_to_features(client.import_source)
        client.save(update_fields=["features"])


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0009_alter_backgroundjob__exec_state'),
    ]

    operations = [
        migrations.AddField(
            model_name='client',
            name='import_source',
            field=models.CharField(
                choices=[
                    ('none', 'No import'), ('ldap', 'LDAP'),
                    ('msgraph', 'Microsoft Graph'), ('os2mo', 'OS2mo'),
                    ('google', 'Google Workspace'),
                ],
                default='none', max_length=16, verbose_name='import source',
            ),
        ),
        migrations.RunPython(forwards, backwards),
    ]
