# Generated by Django 3.2.11 on 2022-07-04 11:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('os2datascanner', '0082_auto_20220622_1137'),
    ]

    operations = [
        migrations.AddField(
            model_name='scanner',
            name='only_notify_superadmin',
            field=models.BooleanField(default=False, verbose_name='Underret kun superadmin'),
        ),
    ]