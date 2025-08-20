from django.db import migrations, models


def create_scanner_references(apps, schema_editor):
    DocumentReport = apps.get_model('os2datascanner_report', 'DocumentReport')
    ScannerReference = apps.get_model('os2datascanner_report', 'ScannerReference')
    Organization = apps.get_model('organizations', 'Organization')

    scanner_info = DocumentReport.objects.values("scanner_job_pk", "scanner_job_name", "organization").annotate(count=models.Count("scanner_job_name"))
    for sc in scanner_info:
        if not sc['scanner_job_pk']:
            continue
        sc_rf, _ = ScannerReference.objects.update_or_create(
            scanner_pk=sc["scanner_job_pk"],
            defaults={
                'scanner_name': sc["scanner_job_name"],
                'organization': Organization.objects.get(uuid=sc["organization"]) if sc["organization"] else None,
            }
        )
        DocumentReport.objects.filter(scanner_job_pk=sc["scanner_job_pk"]).update(scanner_job=sc_rf)


def reverse(apps, schema_editor):
    DocumentReport = apps.get_model('os2datascanner_report', 'DocumentReport')
    ScannerReference = apps.get_model('os2datascanner_report', 'ScannerReference')

    for sc_rf in ScannerReference.objects.iterator():
        DocumentReport.objects.filter(scanner_job=sc_rf).update(
            scanner_job_pk=sc_rf.scanner_pk,
            scanner_job_name=sc_rf.scanner_name,
        )


class Migration(migrations.Migration):

    dependencies = [
        ('os2datascanner_report', '0086_scannerreference_and_more'),
    ]

    operations = [
        migrations.RunPython(
            create_scanner_references,
            reverse_code=reverse,
        ),
    ]
