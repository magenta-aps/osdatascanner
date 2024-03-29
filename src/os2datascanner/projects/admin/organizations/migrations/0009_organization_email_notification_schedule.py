# Generated by Django 3.2.11 on 2022-09-06 13:52

from django.db import migrations
import recurrence.fields


class Migration(migrations.Migration):

    dependencies = [
        ('organizations', '0008_alter_alias'),
    ]

    operations = [
        migrations.AddField(
            model_name='organization',
            name='email_notification_schedule',
            field=recurrence.fields.RecurrenceField(blank=True, max_length=1024, null=True,
                                                    default="RRULE:FREQ=WEEKLY;BYDAY=FR",
                                                    verbose_name='Email notification interval'),
        ),
    ]
