# Generated by Django 3.2.11 on 2025-03-17 06:30

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('organizations', '0052_add_account_permissions_and_syncedpermission_model'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='syncedpermission',
            options={'permissions': [('test', 'Test')]},
        ),
    ]
