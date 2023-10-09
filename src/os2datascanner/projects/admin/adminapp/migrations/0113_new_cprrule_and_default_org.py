# Generated by Django 3.2.11 on 2023-10-09 08:54

from django.db import migrations

from os2datascanner.engine2.rules.cpr import CPRRule
from os2datascanner.projects.admin.adminapp.models.sensitivity_level import (
    Sensitivity,
)


def create_default_cprrule_and_organization(apps, schema_editor):
    Organization = apps.get_model("organizations", "Organization")
    CPRRuleModel = apps.get_model("os2datascanner", "CPRRule")
    CustomRule = apps.get_model("os2datascanner", "CustomRule")

    Organization.objects.get_or_create(
        name="OS2datascanner",
        contact_email="info@magenta-aps.dk",
        contact_phone="+45 3336 9696")

    CPRRuleModel.objects.filter(name="CPR regel").delete()

    CustomRule.objects.get_or_create(
        name="CPR regel",
        description="Denne regel finder alle gyldige CPR numre.",
        sensitivity=Sensitivity.CRITICAL,
        _rule=CPRRule(
            modulus_11=True,
            ignore_irrelevant=True,
            examine_context=True).to_json_object())

    print("SUCCESS! Default organization: 'OS2datascanner'"
          " and default rule: 'CPR Regel' exists in the database.")


class Migration(migrations.Migration):

    dependencies = [
        ('os2datascanner', '0112_turbohealthrule'),
    ]

    operations = [
        migrations.RunPython(
            create_default_cprrule_and_organization,
            reverse_code=migrations.RunPython.noop)
    ]
