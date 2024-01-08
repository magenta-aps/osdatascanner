from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('os2datascanner', '0117_move_rules_to_rule_fields'),
    ]
    
    operations = [
        migrations.AlterField(
            model_name='scanner',
            name='rule',
            field=models.ForeignKey(null=False, on_delete=django.db.models.deletion.PROTECT, related_name='scanners', to='os2datascanner.rule', verbose_name='rule'),
        ),
        migrations.RemoveField(
            model_name='scanner',
            name='exclusion_rules',
        ),
        migrations.RemoveField(
            model_name='scanner',
            name='rules',
        ),
    ]