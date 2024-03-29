# Generated by Django 2.2.10 on 2020-06-12 07:55

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('os2datascanner', '0029_delete_scan_and_friends'),
    ]

    operations = [
        migrations.CreateModel(
            name='DropboxScanner',
            fields=[
                ('scanner_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='os2datascanner.Scanner')),
                ('token', models.CharField(max_length=64, null=True, validators=[django.core.validators.MinLengthValidator(64)], verbose_name='Token')),
            ],
            bases=('os2datascanner.scanner',),
        ),
    ]



