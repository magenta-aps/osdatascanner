# Generated by Django 3.2.11 on 2024-01-29 12:12

from django.db import migrations


def clear_non_relevant_covered_account(apps, schema_editor) -> None:
    CoveredAccount = apps.get_model("os2datascanner", "CoveredAccount")
    Scanner = apps.get_model("os2datascanner", "Scanner")

    CoveredAccount.objects.filter(
        scanner__in=Scanner.objects.filter(
            org_unit__isnull=True)
    ).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('os2datascanner', '0121_alter_coveredaccount_scan_status'),
    ]

    operations = [
        migrations.RunPython(clear_non_relevant_covered_account,
                             reverse_code=migrations.RunPython.noop)
    ]
