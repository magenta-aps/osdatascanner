# Generated by Django 3.2.11 on 2024-12-13 07:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('os2datascanner', '0139_usererrorlog_rename_removed_field_add_resolved_permission'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='scanstatus',
            options={'get_latest_by': 'scan_tag__time', 'permissions': [('resolve_scanstatus', 'Can resolve scan statuses'), ('export_completed_scanstatus', 'Can export history of completed scans')], 'verbose_name': 'scan status', 'verbose_name_plural': 'scan statuses'},
        ),
    ]