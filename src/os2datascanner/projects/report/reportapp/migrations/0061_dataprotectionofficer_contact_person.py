# Generated by Django 3.2.11 on 2022-09-23 10:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('os2datascanner_report', '0060_alter_documentreport_resolution_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='dataprotectionofficer',
            name='contact_person',
            field=models.BooleanField(default=False, verbose_name='Contact Person'),
        ),
    ]
