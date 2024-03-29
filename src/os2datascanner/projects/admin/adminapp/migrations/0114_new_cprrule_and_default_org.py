# Generated by Django 3.2.11 on 2023-11-17 08:54

from django.db import migrations

from os2datascanner.engine2.rules.cpr import CPRRule
from os2datascanner.projects.admin.adminapp.models.sensitivity_level import (
    Sensitivity,
)


def create_default_cprrule_and_organization(apps, schema_editor):
    CPRRuleModel = apps.get_model("os2datascanner", "CPRRule")
    CustomRule = apps.get_model("os2datascanner", "CustomRule")
    Scanner = apps.get_model("os2datascanner", "Scanner")

    # Get the default organization which should be the owner of the CPR rule.
    # default_org = get_default_organization(apps, schema_editor)

    # Get the old CPR rule and select the scanner jobs that use it.
    old_cpr = CPRRuleModel.objects.filter(name="CPR regel").first()
    if old_cpr is not None:
        jobs = list(Scanner.objects.filter(rules=old_cpr))
        old_cpr.delete()

    if CustomRule.objects.filter(name="CPR regel").first() is None:
        new_cpr = CustomRule.objects.create(
            name="CPR regel",
            description="Denne regel finder alle gyldige CPR numre.",
            sensitivity=Sensitivity.CRITICAL,
            _rule=CPRRule(
                modulus_11=True,
                ignore_irrelevant=True,
                examine_context=True,
            ).to_json_object())

        # If there are any jobs that used the old cpr rule
        # add the new one instead.
        for job in ('jobs' in locals() and jobs or []):
            job.rules.add(new_cpr)

    print("SUCCESS! Default rule: 'CPR Regel' created as CustomRule model in the database.")


def undo_creation_of_cpr_as_customrule(apps, schema_editor):
    CPRRuleModel = apps.get_model("os2datascanner", "CPRRule")
    CustomRule = apps.get_model("os2datascanner", "CustomRule")
    Scanner = apps.get_model("os2datascanner", "Scanner")

    cpr_custom = CustomRule.objects.filter(name="CPR regel").first()
    if cpr_custom is not None:
        jobs = list(Scanner.objects.filter(rules=cpr_custom))
        cpr_custom.delete()

    old_cpr = CPRRule.objects.first()
    if old_cpr is None:
        old_cpr = CPRRule.objects.create(
            name="CPR regel",
            description="Denne regel finder alle gyldige CPR numre.",
            sensitivity=Sensitivity.CRITICAL,
            do_modulus11=True,
            ignore_irrelevant=True,
            examine_context=True,
        )

    for job in ('jobs' in locals() and jobs or []):
        jobs.rules.add(old_cpr)

    print("SUCCESS! Default rule: 'CPR Regel' created as CPRRule model in the database.")


class Migration(migrations.Migration):

    dependencies = [
        ('os2datascanner', '0113_scanner_keep_false_positives'),
    ]

    operations = [
        migrations.RunPython(
            create_default_cprrule_and_organization,
            reverse_code=undo_creation_of_cpr_as_customrule)
    ]
