# Generated by Django 3.2.11 on 2025-04-28 11:54

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('grants', '0013_add_last_updated'),
        ('os2datascanner', '0157_add_grant_permissions_to_groups'),
    ]

    operations = [
        migrations.CreateModel(
            name='MSGraphSharepointScanner',
            fields=[
                ('scanner_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='os2datascanner.scanner')),
                ('scan_lists', models.BooleanField(default=False, verbose_name='scan lists')),
                ('scan_drives', models.BooleanField(default=False, verbose_name='scan drives')),
                ('graph_grant', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='grants.graphgrant', verbose_name='Graph grant')),
            ],
            options={
                'verbose_name': 'MSGraph SharePoint scanner',
                'ordering': ['name'],
                'abstract': False,
            },
            bases=('os2datascanner.scanner',),
        ),
    ]
