from django.db import migrations


def assign_permissions(apps, schema_editor):
    Group = apps.get_model("auth", "Group")
    Permission = apps.get_model("auth", "Permission")

    superadmins = Group.objects.get(name="superadmins")
    admins = Group.objects.get(name="admins")

    permission = Permission.objects.get(codename="change_permissions_account")

    superadmins.permissions.add(permission)
    admins.permissions.add(permission)


class Migration(migrations.Migration):

    dependencies = [
        ('os2datascanner', '0178_alter_sbsysdbscanner_options'),
    ]

    operations = [
        migrations.RunPython(assign_permissions, reverse_code=migrations.RunPython.noop)
    ]
