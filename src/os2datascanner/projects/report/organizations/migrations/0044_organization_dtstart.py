# Generated by Django 3.2.11 on 2024-09-10 09:08

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('organizations', '0043_outlookcategory_unique_outlook_categories'),
    ]

    operations = [
        migrations.AddField(
            model_name='organization',
            name='dtstart',
            field=models.DateField(default=datetime.date.today, verbose_name='schedule start time'),
        ),
    ]
