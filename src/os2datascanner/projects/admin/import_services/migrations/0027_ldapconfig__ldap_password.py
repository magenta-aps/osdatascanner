# Generated by Django 3.2.11 on 2024-12-17 10:34

from django.db import migrations, models
from django.conf import settings
from os2datascanner.projects.utils import aes

def migrate_ldapconfig_password(apps, schema_editor):
    LDAPConfig = apps.get_model("import_services", "LDAPConfig")

    for ldap_conf in LDAPConfig.objects.iterator():
        if ldap_conf._iv_ldap_credential and ldap_conf._cipher_ldap_credential:

            ldap_pw = aes.decrypt(ldap_conf._iv_ldap_credential,
                                  ldap_conf._cipher_ldap_credential,
                                  key=settings.DECRYPTION_HEX)

            iv, ciphertext = aes.encrypt(
                    ldap_pw, settings.DECRYPTION_HEX)

            ldap_conf._ldap_password = [c.hex() for c in (iv, ciphertext)]

            ldap_conf.save()
        else:
            pass


class Migration(migrations.Migration):

    dependencies = [
        ('import_services', '0026_authenticationflow_flowexecution_identityprovider_idpmappers_keycloakclient'),
    ]

    operations = [
        migrations.AddField(
            model_name='ldapconfig',
            name='_ldap_password',
            field=models.JSONField(null=True, verbose_name='LDAP password (encrypted)'),
        ),
        migrations.RunPython(migrate_ldapconfig_password,
                             reverse_code=migrations.RunPython.noop),
    ]
