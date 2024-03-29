# Generated by Django 3.2.11 on 2023-02-17 13:42

from django.db import migrations, models
import django.db.models.deletion


def populate_m2m(apps, schema_editor):
    DocumentReport = apps.get_model('os2datascanner_report', 'DocumentReport')
    DocumentReportAliasThrough = apps.get_model('os2datascanner_report',
                                                'DocumentReportAliasThrough')

    for dr in DocumentReport.objects.iterator():
        for alias in dr.alias_relation.all():
            DocumentReportAliasThrough.objects.create(alias_id=alias.pk, documentreport_id=dr.pk,
                                                      alias_uuid=alias.uuid)


class Migration(migrations.Migration):
    dependencies = [
        ('os2datascanner_report', '0071_populate_created_timestamp'),
    ]

    operations = [
        migrations.CreateModel(
            name='DocumentReportAliasThrough',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False,
                                        verbose_name='ID')),
                ('alias_uuid', models.UUIDField()),
                ('alias', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                                            related_name='alias_relation',
                                            to='organizations.alias')),
                ('documentreport', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                                                     related_name='match_relation',
                                                     to='os2datascanner_report.documentreport')),
            ],
        ),
        migrations.AddConstraint(
            model_name='DocumentReportAliasThrough',
            constraint=models.UniqueConstraint(fields=('documentreport', 'alias_uuid'),
                                               name='unique_alias_documentreport'),
        ),
        migrations.AddField(
            model_name='documentreport',
            name='temp_alias_relation',
            field=models.ManyToManyField(through='os2datascanner_report.DocumentReportAliasThrough',
                                         to='organizations.Alias'),
        ),
        migrations.RunPython(populate_m2m, reverse_code=migrations.RunPython.noop)
    ]
