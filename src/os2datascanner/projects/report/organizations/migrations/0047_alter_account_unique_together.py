# Generated by Django 3.2.11 on 2024-10-07 13:07

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('organizations', '0046_account_is_universal_dpo'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='account',
            unique_together={('organization', 'username')},
        ),
    ]
