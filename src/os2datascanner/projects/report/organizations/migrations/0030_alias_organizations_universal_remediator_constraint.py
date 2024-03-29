# Generated by Django 3.2.11 on 2023-11-24 07:13

from django.db import migrations, models


def delete_other_remediator_aliases(apps, schema_editor):
    Account = apps.get_model('organizations', 'Account')

    for acc in Account.objects.iterator():
        # If the account is a universal remediator ...
        if acc.aliases.filter(_alias_type="remediator", _value=0).exists():
            # Delete all other remediator aliases for that account
            acc.aliases.filter(_alias_type="remediator").exclude(_value=0).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('organizations', '0029_alter_organizations'),
    ]

    operations = [
        migrations.RunPython(delete_other_remediator_aliases, reverse_code=migrations.RunPython.noop),
    ]
