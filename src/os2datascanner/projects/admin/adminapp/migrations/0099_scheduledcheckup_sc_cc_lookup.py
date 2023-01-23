# Generated by Django 3.2.11 on 2023-01-23 10:12

import django.contrib.postgres.indexes
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('os2datascanner', '0098_msgraphmailscanner_scan_deleted_items_folder'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='scheduledcheckup',
            index=django.contrib.postgres.indexes.HashIndex(fields=['handle_representation'], name='sc_cc_lookup'),
        ),
    ]
