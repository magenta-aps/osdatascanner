# Generated by Django 3.2.11 on 2025-04-08 06:39

from django.db import migrations, models


def set_scan_entire_org(apps, schema_editor):
    model_names = [
        "MSGraphMailScanner",
        "MSGraphFileScanner",
        "MSGraphCalendarScanner",
        "GmailScanner",
        "GoogleDriveScanner",
    ]

    for model_name in model_names:
        model = apps.get_model('os2datascanner', model_name)
        for scanner in model.objects.iterator():
            if not scanner.org_unit.exists():
                scanner.scan_entire_org = True
                scanner.save(update_fields=['scan_entire_org'])


class Migration(migrations.Migration):

    dependencies = [
        ('os2datascanner', '0155_gmail_add_scan_attachments'),
    ]

    operations = [
        migrations.AddField(
            model_name='scanner',
            name='scan_entire_org',
            field=models.BooleanField(default=False, verbose_name='scan all accounts in organization'),
        ),
        migrations.RunPython(
            set_scan_entire_org,
            reverse_code=migrations.RunPython.noop
        ),
    ]
