# Generated by Django 3.2.11 on 2024-12-02 08:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('os2datascanner', '0136_alter_scanner_options'),
    ]

    operations = [
        migrations.AddField(
            model_name='scanner',
            name='removed',
            field=models.BooleanField(default=False, verbose_name='removed'),
        ),
    ]
