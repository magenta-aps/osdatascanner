# Generated by Django 2.2.10 on 2021-03-01 12:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('os2datascanner_report', '0023_adds_role_dataprotection_officer'),
    ]

    operations = [
        migrations.AddField(
            model_name='documentreport',
            name='resolution_time',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]



