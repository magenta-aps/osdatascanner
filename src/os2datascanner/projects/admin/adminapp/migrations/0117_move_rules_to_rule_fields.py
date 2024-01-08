from django.db import migrations, models
import django.db.models.deletion

from os2datascanner.utils.system_utilities import time_now

def set_rule(apps, schema_editor):
    CustomRule = apps.get_model('os2datascanner', 'CustomRule')
    Scanner = apps.get_model('os2datascanner', 'Scanner')

    for scanner in Scanner.objects.iterator():
        if scanner.rules.count() > 1:
            # The scanner has multiple rules. Create a new rule that combines all
            # existing rules.
            date_stamp = time_now().strftime('%y-%m-%d')
            rules = scanner.rules.all()
            new_rule, _ = CustomRule.objects.get_or_create(
                name=f"{date_stamp} - Migration rule ({', '.join([str(rule.pk) for rule in rules])})", 
                defaults={
                "description": f"OrRule that combines the rules: {', '.join([f'{rule.name} ({rule.pk})' for rule in rules])}",
                "_rule": {"type": "or", "components": [rule.customrule._rule for rule in rules]},
                "organization": scanner.organization
                }
                )
            scanner.rule = new_rule
            scanner.save()
        elif scanner.rules.count() == 1:
            # The scanner has one rule. Use that.
            scanner.rule = scanner.rules.first()
            scanner.save()
        else:
            # The scanner has no rules. Create a dummy rule and use that.
            date_stamp = time_now().strftime('%y-%m-%d')
            dummy_rule, _ = CustomRule.objects.get_or_create(
                name=f"{date_stamp} - Dummy rule", 
                defaults={
                    "description": "Dummy rule created as a part of migration to new rule field, since no rules could be succesfully moved from old rules field.",
                    "_rule": {},
                    "organization": scanner.organization
                    }
                )
            scanner.rule = dummy_rule
            scanner.save()

def set_exclusion_rule(apps, schema_editor):
    CustomRule = apps.get_model('os2datascanner', 'CustomRule')
    Scanner = apps.get_model('os2datascanner', 'Scanner')

    for scanner in Scanner.objects.iterator():
        if scanner.exclusion_rules.count() > 1:
            # The scanner has multiple exclusion rules. Create a new rule that 
            # combines all existing rules.
            date_stamp = time_now().strftime('%y-%m-%d')
            rules = scanner.exclusion_rules.all()
            new_rule, _ = CustomRule.objects.get_or_create(
                name=f"{date_stamp} - Migration rule ({', '.join([str(rule.pk) for rule in rules])})", 
                defaults={
                    "description": f"OrRule that combines the rules: {', '.join([f'{rule.name} ({rule.pk})' for rule in rules])}",
                    "_rule": {"type": "or", "components": [rule.customrule._rule for rule in rules]},
                    "organization": scanner.organization
                    }
                )
            scanner.exclusion_rule = new_rule
            scanner.save()
        elif scanner.exclusion_rules.count() == 1:
            # The scanner has one exclusion rule. Use that.
            scanner.exclusion_rule = scanner.exclusion_rules.first()
            scanner.save()
        else:
            # The scanner has no exclusion rules. Don't add any.
            pass

def revert_rule_to_rules(apps, schema_editor):
    Scanner = apps.get_model('os2datascanner', 'Scanner')
    for scanner in Scanner.objects.iterator():
        scanner.rules.add(scanner.rule)

def revert_exclusion_rule_to_exclusion_rules(apps, schema_editor):
    Scanner = apps.get_model('os2datascanner', 'Scanner')
    for scanner in Scanner.objects.iterator():
        if scanner.exclusion_rule:
            scanner.exclusion_rules.add(scanner.exclusion_rule)


class Migration(migrations.Migration):

    dependencies = [
        ('os2datascanner', '0116_add_scanner_rule_and_exclusion_rule_fields'),
    ]
    
    operations = [
        migrations.RunPython(set_rule, reverse_code=revert_rule_to_rules),
        migrations.RunPython(set_exclusion_rule, reverse_code=revert_exclusion_rule_to_exclusion_rules),
    ]