# Generated by Django 3.2.11 on 2024-10-22 10:57

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('organizations', '0046_account_is_universal_dpo'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='account',
            name='handled_matches',
        ),
        migrations.RemoveField(
            model_name='account',
            name='match_count',
        ),
        migrations.RemoveField(
            model_name='account',
            name='match_status',
        ),
        migrations.RemoveField(
            model_name='account',
            name='withheld_matches',
        ),
    ]
