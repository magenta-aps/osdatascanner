from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('grants', '0019_grant_base_link'),
    ]

    operations = [
        # We can no longer have these constraints, since they depend on fields now on parent-model.
        migrations.RemoveConstraint(
            model_name='ewsgrant',
            name='grants_ewsgrant_unique',
        ),
        migrations.RemoveConstraint(
            model_name='graphgrant',
            name='avoid_multiple_overlapping_grants',
        ),
        migrations.RemoveConstraint(
            model_name='smbgrant',
            name='grants_smbgrant_unique',
        ),
        # These fields are now gone from child models.
        migrations.RemoveField(model_name='ewsgrant', name='uuid'),
        migrations.RemoveField(model_name='ewsgrant', name='last_updated'),
        migrations.RemoveField(model_name='ewsgrant', name='organization'),
        migrations.RemoveField(model_name='googleapigrant', name='uuid'),
        migrations.RemoveField(model_name='googleapigrant', name='last_updated'),
        migrations.RemoveField(model_name='googleapigrant', name='organization'),
        migrations.RemoveField(model_name='graphgrant', name='uuid'),
        migrations.RemoveField(model_name='graphgrant', name='last_updated'),
        migrations.RemoveField(model_name='graphgrant', name='organization'),
        migrations.RemoveField(model_name='smbgrant', name='uuid'),
        migrations.RemoveField(model_name='smbgrant', name='last_updated'),
        migrations.RemoveField(model_name='smbgrant', name='organization'),

        # Alter OneToOneFields to be non-nullable / real pointer relations.
        migrations.AlterField(
            model_name='ewsgrant',
            name='grant_ptr',
            field=models.OneToOneField(
                to='grants.grant',
                on_delete=django.db.models.deletion.CASCADE,
                parent_link=True,
                primary_key=True,
                serialize=False,
                auto_created=True,
            ),
        ),
        migrations.AlterField(
            model_name='googleapigrant',
            name='grant_ptr',
            field=models.OneToOneField(
                to='grants.grant',
                on_delete=django.db.models.deletion.CASCADE,
                parent_link=True,
                primary_key=True,
                serialize=False,
                auto_created=True,
            ),
        ),
        migrations.AlterField(
            model_name='graphgrant',
            name='grant_ptr',
            field=models.OneToOneField(
                to='grants.grant',
                on_delete=django.db.models.deletion.CASCADE,
                parent_link=True,
                primary_key=True,
                serialize=False,
                auto_created=True,
            ),
        ),
        migrations.AlterField(
            model_name='smbgrant',
            name='grant_ptr',
            field=models.OneToOneField(
                to='grants.grant',
                on_delete=django.db.models.deletion.CASCADE,
                parent_link=True,
                primary_key=True,
                serialize=False,
                auto_created=True,
            ),
        ),
    ]
