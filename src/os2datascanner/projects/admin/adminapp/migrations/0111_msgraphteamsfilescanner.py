# Generated by Django 3.2.11 on 2023-07-05 10:56

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('grants', '0001_initial'),
        ('os2datascanner', '0110_change_enabled_scans'),
    ]

    operations = [
        migrations.CreateModel(
            name='MSGraphTeamsFileScanner',
            fields=[
                ('scanner_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='os2datascanner.scanner')),
                ('do_link_check', models.BooleanField(default=False, verbose_name='check dead links')),
                ('grant', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='grants.graphgrant')),
            ],
            options={
                'ordering': ['name'],
                'abstract': False,
            },
            bases=('os2datascanner.scanner',),
        ),
    ]
