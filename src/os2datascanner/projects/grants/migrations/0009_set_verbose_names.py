# Generated by Django 3.2.11 on 2025-01-24 12:45

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('grants', '0008_graphgrant_expiry_date'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='ewsgrant',
            options={'verbose_name': 'EWS Service Account Grant'},
        ),
        migrations.AlterModelOptions(
            name='graphgrant',
            options={'verbose_name': 'Microsoft Graph Grant'},
        ),
        migrations.AlterModelOptions(
            name='smbgrant',
            options={'verbose_name': 'SMB Service Account Grant'},
        ),
    ]
