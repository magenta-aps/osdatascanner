# Generated by Django 3.2.11 on 2024-10-29 10:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('organizations', '0048_trigram_extension'),
    ]

    operations = [
        migrations.AddField(
            model_name='organizationalunit',
            name='hidden',
            field=models.BooleanField(default=False, verbose_name='hidden'),
        ),
    ]
