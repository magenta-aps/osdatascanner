# Generated by Django 3.2.11 on 2024-12-18 10:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('import_services', '0027_ldapconfig__ldap_password'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='ldapconfig',
            name='_cipher_ldap_credential',
        ),
        migrations.RemoveField(
            model_name='ldapconfig',
            name='_iv_ldap_credential',
        ),
        migrations.AlterField(
            model_name='ldapconfig',
            name='_ldap_password',
            field=models.JSONField(verbose_name='LDAP password (encrypted)'),
        ),
    ]