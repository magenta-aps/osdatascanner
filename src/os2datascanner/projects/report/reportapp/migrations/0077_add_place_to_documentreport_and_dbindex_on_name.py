# Generated by Django 3.2.11 on 2023-06-08 06:50

from django.db import migrations, models

from os2datascanner.engine2.model.core import Handle


def populate_place_fields_of_documentreports(apps, schema_editor):
    DocumentReport = apps.get_model('os2datascanner_report', 'DocumentReport')

    all_reports = DocumentReport.objects.all()
    for dr in all_reports.filter(raw_matches__isnull=False).iterator():
        handle = Handle.from_json_object(dr.raw_matches['handle'])
        dr.place =  handle.presentation_place
        dr.save()


class Migration(migrations.Migration):

    dependencies = [
        ('os2datascanner_report', '0076_alias_creation_index'),
    ]

    operations = [
        migrations.AddField(
            model_name='documentreport',
            name='place',
            field=models.CharField(db_index=True, default='', max_length=256, verbose_name='place'),
        ),
        migrations.AlterField(
            model_name='documentreport',
            name='name',
            field=models.CharField(db_index=True, default='', max_length=256, verbose_name='name'),
        ),
    ]
