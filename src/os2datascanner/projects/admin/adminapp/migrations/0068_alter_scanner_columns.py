# Generated by Django 3.2.4 on 2021-09-30 09:52

import django.core.validators
from django.db import migrations, models
import re


class Migration(migrations.Migration):

    dependencies = [
        ('os2datascanner', '0067_scanstatus_last_modified'),
    ]

    operations = [
        migrations.AlterField(
            model_name='scanner',
            name='columns',
            field=models.CharField(blank=True, max_length=128, null=True, validators=[django.core.validators.RegexValidator(re.compile('^\\d+(?:,\\d+)*\\Z'), code='invalid', message='Enter only digits separated by commas.')]),
        ),
    ]
