# Generated by Django 3.2.11 on 2022-11-17 13:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('organizations', '0010_alter_position_unit'),
    ]

    operations = [
        migrations.AddField(
            model_name='account',
            name='matchcount',
            field=models.IntegerField(blank=True, default=0, null=True, verbose_name='Number of matches'),
        ),
    ]
