from django.db import migrations
from django.contrib.auth.management import create_permissions


def migrate_permissions(apps, schema_editor):
    """Create Permission-objects now instead of post-migration."""
    for app_config in apps.get_app_configs():
        app_config.models_module = True
        create_permissions(app_config, apps=apps, verbosity=0)
        app_config.models_module = None


def create_groups(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Group.objects.get_or_create(name="admins")
    Group.objects.get_or_create(name="superadmins")


def assign_permissions(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Permission = apps.get_model('auth', 'Permission')

    admins = Group.objects.get(name="admins")
    superadmins = Group.objects.get(name="superadmins")

    admin_permissions = Permission.objects.filter(codename__in=[
        "export_completed_scanstatus",
        "hide_scanner",
        "add_scanner",
        "change_scanner",
        "resolve_scanstatus",
        "delete_scanstatus",
        "view_organizationalunit",
        "change_visibility_organizationalunit",
        "change_organization"
    ])

    superadmin_permissions = Permission.objects.filter(codename__in=[
        "view_client",
        "add_organization",
        "delete_organization",
        "can_validate"
    ])

    admins.permissions.add(*admin_permissions)
    superadmins.permissions.add(*superadmin_permissions)


def delete_groups(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Group.objects.filter(
        name__in=[
            "admins", "superadmins"
        ]
    ).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('os2datascanner', '0143_add_scanner_verbose_names'),
    ]

    operations = [
        migrations.RunPython(create_groups, reverse_code=delete_groups),
        # Before assigning permissions, they have to exist!
        # Maybe they do, but especially for new installations, _they won't_.
        # We create permissions here, to make sure they exist.
        migrations.RunPython(migrate_permissions, reverse_code=migrations.RunPython.noop),
        migrations.RunPython(assign_permissions, reverse_code=migrations.RunPython.noop)
    ]
