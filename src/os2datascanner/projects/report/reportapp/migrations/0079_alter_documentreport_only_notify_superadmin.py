# Generated by Django 3.2.11 on 2023-09-19 06:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('os2datascanner_report', '0078_delete_dataprotectionofficer'),
    ]

    operations = [
        migrations.AlterField(
            model_name='documentreport',
            name='only_notify_superadmin',
            field=models.BooleanField(db_index=True, default=False, verbose_name='Underret kun superadmin'),
        ),
    ]
