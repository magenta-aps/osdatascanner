# Generated by Django 2.2.18 on 2021-03-18 12:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('os2datascanner_report', '0027_documentreport_source_type'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='dataprotectionofficer',
            options={'verbose_name': 'DPO', 'verbose_name_plural': 'DPOs'},
        ),
        migrations.AlterField(
            model_name='documentreport',
            name='source_type',
            field=models.CharField(max_length=2000, verbose_name='source type'),
        ),
    ]



