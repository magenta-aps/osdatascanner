# Generated by Django 2.2.4 on 2019-11-18 13:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('os2datascanner', '0016_bigint_statistics'),
    ]

    operations = [
        migrations.AddField(
            model_name='scanner',
            name='e2_last_run_at',
            field=models.DateTimeField(null=True),
        ),
    ]



