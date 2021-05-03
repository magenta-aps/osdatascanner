# Generated by Django 2.2.18 on 2021-05-03 10:46

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('os2datascanner', '0051_delete_old_organization'),
    ]

    operations = [
        migrations.RenameField(
            model_name='apikey',
            old_name='ldap_organization',
            new_name='organization',
        ),
        migrations.RenameField(
            model_name='rule',
            old_name='ldap_organization',
            new_name='organization',
        ),
        migrations.RenameField(
            model_name='scanner',
            old_name='ldap_organization',
            new_name='organization',
        ),
    ]
