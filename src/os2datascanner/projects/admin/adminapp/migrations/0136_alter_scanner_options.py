# Generated by Django 3.2.11 on 2024-11-07 08:58

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('os2datascanner', '0135_scanstatus_email_sent'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='scanner',
            options={'ordering': ['name'], 'permissions': [('can_validate', 'Can validate scannerjobs')]},
        ),
    ]
