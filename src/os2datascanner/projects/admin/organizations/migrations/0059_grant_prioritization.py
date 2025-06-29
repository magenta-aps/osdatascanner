# Generated by Django 5.2.1 on 2025-06-19 08:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('organizations', '0058_alter_alias_shared'),
    ]

    operations = [
        migrations.AddField(
            model_name='organization',
            name='prioritize_graphgrant',
            field=models.BooleanField(default=False, help_text='prioritize a Microsoft Graph Grant over an EWS Service Account for example when using Exchange online rather than Exchange on-premises', verbose_name='Prioritize MSGraph grant'),
        ),
    ]
