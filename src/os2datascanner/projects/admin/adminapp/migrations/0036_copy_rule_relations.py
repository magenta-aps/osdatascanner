from django.db import migrations


class Migration(migrations.Migration):

    def forwards_func(apps, schema_editor):
        Scannerjob = apps.get_model('os2datascanner', 'Scanner')
        OrderedRule = apps.get_model('os2datascanner', 'OrderedRule')
        sj = Scannerjob.objects.all()
        ordered_rules = []
        for s in sj:
            rules = s.rules.all()
            for pos, rule in enumerate(rules):
                ordered_rules.append(
                    OrderedRule(
                        rule=rule,
                        scanner_job=s,
                        position=pos,
                    )
                )
        OrderedRule.objects.bulk_create(ordered_rules)

    def reverse_func(apps, schema_editor):
        pass

    dependencies = [
        ('os2datascanner', '0035_orderedrule'),
    ]

    operations = [
        migrations.RunPython(forwards_func, reverse_func),
    ]
