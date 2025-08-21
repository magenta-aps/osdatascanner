import django.db.models.deletion
from django.db import migrations, models


def update_reports_without_scanners(apps, schema_editor):
    DocumentReport = apps.get_model('os2datascanner_report', 'DocumentReport')
    ScannerReference = apps.get_model('os2datascanner_report', 'ScannerReference')

    orphan_reports = DocumentReport.objects.filter(scanner_job__isnull=True)
    if orphan_reports.exists():
        sr = ScannerReference.objects.create(
            scanner_pk=260504,
            scanner_name="dummy_migration_scanner_reference",
        )
        orphan_reports.update(scanner_job=sr)

def update_scanners_without_org(apps, schema_editor):
    DocumentReport = apps.get_model('os2datascanner_report', 'DocumentReport')
    ScannerReference = apps.get_model('os2datascanner_report', 'ScannerReference')
    Organization = apps.get_model('organizations', 'Organization')

    for sr in ScannerReference.objects.filter(organization__isnull=True).iterator():
        if (dr := sr.document_reports.filter(organization__isnull=False).first()) is not None:
            sr.organization = dr.organization
            sr.save()

    orphan_scanners = ScannerReference.objects.filter(organization__isnull=True)
    if orphan_scanners.exists():
        org = Organization.objects.create(name="dummy_migration_organization")
        orphan_scanners.update(organization=org)


class Migration(migrations.Migration):
    dependencies = [
        ('organizations', '0062_alter_organization_exchange_delete_permission_and_more'),
        ('os2datascanner_report', '0088_remove_documentreport_unique_scanner_pk_and_path_and_more'),
    ]
    operations = [
        migrations.RunPython(
            update_reports_without_scanners,
            reverse_code=migrations.RunPython.noop,
        ),
        migrations.RunPython(
            update_scanners_without_org,
            reverse_code=migrations.RunPython.noop,
        ),
    ]
