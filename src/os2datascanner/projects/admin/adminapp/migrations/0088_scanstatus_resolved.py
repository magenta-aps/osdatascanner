# Generated by Django 3.2.11 on 2022-09-13 10:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('os2datascanner', '0087_usererrorlog_is_removed'),
    ]

    operations = [
        migrations.AddField(
            model_name='scanstatus',
            name='resolved',
            field=models.BooleanField(default=False, verbose_name='resolved'),
        ),
    ]
