# Generated by Django 3.2.11 on 2025-04-09 08:19

from django.db import migrations, models
import django.db.models.constraints


class Migration(migrations.Migration):

    dependencies = [
        ('organizations', '0052_syncedpermission_model'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='account',
            unique_together=set(),
        ),
        migrations.AddConstraint(
            model_name='account',
            constraint=models.UniqueConstraint(deferrable=django.db.models.constraints.Deferrable['DEFERRED'], fields=('organization', 'username'), name='unique_org_username'),
        ),
    ]
