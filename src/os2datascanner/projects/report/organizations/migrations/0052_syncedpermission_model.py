# Generated by Django 3.2.11 on 2025-01-30 07:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('organizations', '0051_organization_retention_policy_and_value'),
    ]

    operations = [
        migrations.CreateModel(
            name='SyncedPermission',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'abstract': False,
                'permissions': []
            },
        ),
        migrations.AddField(
            model_name='account',
            name='permissions',
            field=models.ManyToManyField(blank=True, limit_choices_to={'content_type__model': 'syncedpermission'}, to='auth.Permission', verbose_name='account permissions'),
        ),
    ]
