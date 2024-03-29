# Generated by Django 3.2.4 on 2021-10-14 12:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('os2datascanner_report', '0036_documentreport_scanner_job_pk'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='documentreport',
            constraint=models.UniqueConstraint(fields=('scanner_job_pk', 'path'), name='unique_scanner_pk_and_path'),
        ),
    ]
