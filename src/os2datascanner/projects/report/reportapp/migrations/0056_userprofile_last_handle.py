# Generated by Django 3.2.11 on 2022-08-12 11:32

from django.db import migrations, models


def create_profiles_for_all_users(apps, schema_editor):
    UserProfile = apps.get_model("os2datascanner_report", "UserProfile")
    User = apps.get_model("auth", "User")
    Organization = apps.get_model("organizations", "Organization")


    if Organization.objects.count() == 1:
        related_org = Organization.objects.first()
    else:
        related_org = None

    for user in User.objects.iterator():
        UserProfile.objects.update_or_create(user=user, defaults={'organization': related_org})




class Migration(migrations.Migration):

    dependencies = [
        ('os2datascanner_report', '0055_alter_defaultrole_options'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='last_handle',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Sidste håndtering'),
        ),
        migrations.RunPython(create_profiles_for_all_users, reverse_code=migrations.RunPython.noop)
    ]
