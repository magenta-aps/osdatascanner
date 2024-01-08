from django.db import migrations, models
import django.db.models.deletion

from os2datascanner.utils.system_utilities import time_now

def set_rule(apps, schema_editor):
    CustomRule = apps.get_model('os2datascanner', 'CustomRule')
    Scanner = apps.get_model('os2datascanner', 'Scanner')

    for scanner in Scanner.objects.iterator():
        print("\nScanner pk:", scanner.pk)
        if scanner.rules.count() > 1:
            print(f"Scanner '{scanner}' has more than one connected rule! Creating a new rule.")
            date_stamp = time_now().strftime('%y%m%d')
            rules = scanner.rules.all()
            new_rule, _ = CustomRule.objects.get_or_create(
                name=f"{date_stamp} - Migration rule ({', '.join([str(rule.pk) for rule in rules])})", 
                description=f"OrRule that combines the rules: {', '.join([f'{rule.name} ({rule.pk})' for rule in rules])}",
                _rule={"type": "or", "compontents": [rule.customrule._rule for rule in rules]}
            )
            scanner.rule = new_rule
            scanner.save()
        else:
            scanner.rule = scanner.rules.first()
            scanner.save()

def set_exclusion_rule(apps, schema_editor):
    CustomRule = apps.get_model('os2datascanner', 'CustomRule')
    Scanner = apps.get_model('os2datascanner', 'Scanner')

    for scanner in Scanner.objects.iterator():
        if scanner.exclusion_rules.count() > 1:
            print(f"Scanner '{scanner}' has more than one connected rule! Creating a new rule.")
            date_stamp = time_now().strftime('%y%m%d')
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
        else:
            scanner.exclusion_rule = scanner.exclusion_rules.first()
            scanner.save()

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