# Generated by Django 3.2.11 on 2024-02-16 12:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('organizations', '0025_granulate_org_outlook_settings'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='organization',
            name='msgraph_write_permissions',
        ),
    ]
