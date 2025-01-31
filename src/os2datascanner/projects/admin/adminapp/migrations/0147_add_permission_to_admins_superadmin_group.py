from django.db import migrations


def assign_permissions(apps, schema_editor):
    Group = apps.get_model("auth", "Group")
    Permission = apps.get_model("auth", "Permission")

    groups = Group.objects.filter(name__in=["admins", "superadmins"])

    permission = Permission.objects.get(codename="change_user")

    for group in groups:
        group.permissions.add(permission)


class Migration(migrations.Migration):

    dependencies = [
        ('os2datascanner', '0146_scanner_contact_person'),
    ]

    operations = [
        migrations.RunPython(assign_permissions, reverse_code=migrations.RunPython.noop)
    ]