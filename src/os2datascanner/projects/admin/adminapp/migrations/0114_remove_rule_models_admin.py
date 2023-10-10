# Generated by Django 3.2.11 on 2023-10-10 10:50

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('os2datascanner', '0113_new_cprrule_and_default_org'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cprrule',
            name='rule_ptr',
        ),
        migrations.RemoveField(
            model_name='namerule',
            name='rule_ptr',
        ),
        migrations.RemoveField(
            model_name='regexpattern',
            name='regex',
        ),
        migrations.RemoveField(
            model_name='regexrule',
            name='rule_ptr',
        ),
        migrations.RemoveField(
            model_name='turbocprrule',
            name='rule_ptr',
        ),
        migrations.RemoveField(
            model_name='turbohealthrule',
            name='rule_ptr',
        ),
        migrations.DeleteModel(
            name='AddressRule',
        ),
        migrations.DeleteModel(
            name='CPRRule',
        ),
        migrations.DeleteModel(
            name='NameRule',
        ),
        migrations.DeleteModel(
            name='RegexPattern',
        ),
        migrations.DeleteModel(
            name='RegexRule',
        ),
        migrations.DeleteModel(
            name='TurboCPRRule',
        ),
        migrations.DeleteModel(
            name='TurboHealthRule',
        ),
    ]
