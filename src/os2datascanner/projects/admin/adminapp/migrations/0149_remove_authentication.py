# Generated by Django 3.2.11 on 2025-02-27 14:38

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('os2datascanner', '0148_authentication_to_grant'),
    ]

    operations = [
        migrations.DeleteModel(
            name='AuthenticationMethods',
        ),
        migrations.RemoveField(
            model_name='scanner',
            name='authentication',
        ),
        migrations.DeleteModel(
            name='Authentication',
        ),
    ]
