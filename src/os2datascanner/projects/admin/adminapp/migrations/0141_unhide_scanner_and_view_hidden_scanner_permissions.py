# Generated by Django 3.2.11 on 2025-01-07 07:04

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('os2datascanner', '0140_scanstatus_resolve_permission'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='scanner',
            options={'ordering': ['name'], 'permissions': [('can_validate', 'Can validate scannerjobs'), ('hide_scanner', 'Can hide scannerjob from scannerjob list'), ('unhide_scanner', 'Can unhide scannerjob from the removed scannerjob list'), ('view_hidden_scanner', 'Can view hidden scanners in the removed scannerjob list')]},
        ),
    ]
