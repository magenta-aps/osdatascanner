# Generated by Django 3.2.11 on 2024-10-08 07:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('organizations', '0045_alter_org_support_settings'),
    ]

    operations = [
        migrations.AddField(
            model_name='account',
            name='is_universal_dpo',
            field=models.BooleanField(default=False, verbose_name='universal dpo status'),
        ),
    ]
