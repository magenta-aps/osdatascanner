# Generated by Django 3.2.11 on 2022-06-22 09:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('os2datascanner', '0081_remove_scheduledcheckup_sc_pc_lookup'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='scanner',
            name='exclusion_rules',
        ),
        migrations.AddField(
            model_name='scanner',
            name='exclusion_rules',
            field=models.ManyToManyField(blank=True, related_name='scanners_ex_rules', to='os2datascanner.Rule', verbose_name='Udelukkelsesregler'),
        ),
    ]
