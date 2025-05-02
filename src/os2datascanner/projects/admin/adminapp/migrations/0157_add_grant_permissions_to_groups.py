from django.db import migrations


def assign_permissions(apps, schema_editor):
    Group = apps.get_model("auth", "Group")
    Permission = apps.get_model("auth", "Permission")

    group = Group.objects.get(name="superadmins")

    permissions = Permission.objects.filter(codename__in=["view_graphgrant", "add_graphgrant",
                                                          "delete_graphgrant", "change_graphgrant",
                                                          "view_smbgrant", "add_smbgrant",
                                                          "delete_smbgrant", "change_smbgrant",
                                                          "view_ewsgrant", "add_ewsgrant",
                                                          "delete_ewsgrant", "change_ewsgrant",
                                                          "view_googleapigrant",
                                                          "add_googleapigrant",
                                                          "delete_googleapigrant",
                                                          "change_googleapigrant"]
                                            )
    group.permissions.add(*permissions)


class Migration(migrations.Migration):

    dependencies = [
        ('os2datascanner', '0156_scanner_scan_entire_org'),
    ]

    operations = [
        migrations.RunPython(assign_permissions, reverse_code=migrations.RunPython.noop)
    ]
