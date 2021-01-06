# Generated by Django 2.2.10 on 2020-12-14 19:13

from django.db import migrations, models

from ..utils import iterate_queryset_in_batches, get_max_sens_prop_value


def bulk_update_sensitivity_and_probability_value(apps, schema_editor):
    """See 0011_documentreport_scan_time migration for
    more bulk update information."""
    DocumentReport = apps.get_model("os2datascanner_report", "DocumentReport")
    queryset = DocumentReport.objects.filter(
        data__matches__matched=True)

    bulk_update_by_key(DocumentReport, 'probability', queryset)
    bulk_update_by_key(DocumentReport, 'sensitivity', queryset)


def bulk_update_by_key(DocumentReport, key, queryset):
    for batch in iterate_queryset_in_batches(10000, queryset):
        for dr in batch:
            max_value = get_max_sens_prop_value(dr, key)
            if key == 'probability':
                dr.probability = max_value
            else:
                dr.sensitivity = max_value.value
        DocumentReport.objects.bulk_update(batch, [key])


class Migration(migrations.Migration):

    dependencies = [
        ('os2datascanner_report', '0013_filter_internal_rules_matches'),
    ]

    operations = [
        migrations.AddField(
            model_name='documentreport',
            name='sensitivity',
            field=models.IntegerField(null=True, verbose_name='Sensitivity'),
        ),
        migrations.AddField(
            model_name='documentreport',
            name='probability',
            field=models.FloatField(null=True, verbose_name='Probability'),
        ),
        migrations.RunPython(bulk_update_sensitivity_and_probability_value,
                             reverse_code=migrations.RunPython.noop),
    ]
