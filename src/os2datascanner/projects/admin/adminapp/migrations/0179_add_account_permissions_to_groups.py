from django.db import migrations


def assign_permissions(apps, schema_editor):
    Group = apps.get_model("auth", "Group")
    Permission = apps.get_model("auth", "Permission")

    superadmins = Group.objects.get(name="superadmins")
    admins = Group.objects.get(name="admins")

    permission = Permission.objects.get(codename="change_permissions_account")

    # Add previously missing permission
    superadmins.permissions.add(*admins.permissions.all())

    superadmins.permissions.add(permission)
    admins.permissions.add(permission)


def remove_permissions(apps, schema_editor):
    Group = apps.get_model("auth", "Group")
    Permission = apps.get_model("auth", "Permission")

    superadmins = Group.objects.get(name="superadmins")
    admins = Group.objects.get(name="admins")

    permission = Permission.objects.get(codename="change_permissions_account")

    superadmins.permissions.remove(permission)
    admins.permissions.remove(permission)

    # Remove previously missing permission
    superadmins.permissions.remove(*admins.permissions.all())


class Migration(migrations.Migration):

    dependencies = [
        ('os2datascanner', '0178_alter_sbsysdbscanner_options'),
    ]

    operations = [
        migrations.RunPython(assign_permissions, reverse_code=remove_permissions)
    ]
