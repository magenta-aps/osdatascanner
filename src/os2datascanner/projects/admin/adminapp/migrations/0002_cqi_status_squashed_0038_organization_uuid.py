# Generated by Django 3.2.11 on 2023-10-09 07:26

import django.contrib.postgres.fields.jsonb
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import model_utils.fields
import os2datascanner.projects.admin.adminapp.models.scannerjobs.gmail
import os2datascanner.projects.admin.adminapp.models.scannerjobs.googledrivescanner
import uuid


class Migration(migrations.Migration):

    replaces = [('os2datascanner', '0002_cqi_status'), ('os2datascanner', '0003_related_names'), ('os2datascanner', '0004_scan_order'), ('os2datascanner', '0005_version_mime_type'), ('os2datascanner', '0006_cascade_deleting_scanners'), ('os2datascanner', '0007_version_metadata'), ('os2datascanner', '0008_cprrule'), ('os2datascanner', '0009_concrete_rule'), ('os2datascanner', '0010_scan_rules'), ('os2datascanner', '0011_regexpattern_ordering'), ('os2datascanner', '0012_remove_regexrule_cpr'), ('os2datascanner', '0013_addressrule_namerule'), ('os2datascanner', '0014_remove_special_scan_properties'), ('os2datascanner', '0015_remove_organization_lists'), ('os2datascanner', '0016_bigint_statistics'), ('os2datascanner', '0017_track_scanner_start'), ('os2datascanner', '0018_exchangescanner_service_endpoint'), ('os2datascanner', '0019_purge_old_engine_properties'), ('os2datascanner', '0020_new_sensitivity_level'), ('os2datascanner', '0021_excise_colours'), ('os2datascanner', '0022_delete_conversionqueueitem'), ('os2datascanner', '0023_delete_summary'), ('os2datascanner', '0024_delete_urllastmodified'), ('os2datascanner', '0025_delete_statistics'), ('os2datascanner', '0026_delete_webscan'), ('os2datascanner', '0027_delete_referrerurl'), ('os2datascanner', '0028_delete_webversion'), ('os2datascanner', '0029_delete_scan_and_friends'), ('os2datascanner', '0030_msgraphmailscanner'), ('os2datascanner', '0030_dropboxscanner'), ('os2datascanner', '0030_cprrule_examine_context'), ('os2datascanner', '0031_merge_20200707_1142'), ('os2datascanner', '0032_msgraphfilescanner'), ('os2datascanner', '0033_googledrivescanner'), ('os2datascanner', '0034_gmailscanner'), ('os2datascanner', '0035_scheduledcheckup'), ('os2datascanner', '0036_sbsysscanner'), ('os2datascanner', '0037_scanstatus'), ('os2datascanner', '0038_organization_uuid')]

    dependencies = [
        ('os2datascanner', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='conversionqueueitem',
            name='process_start_time',
            field=model_utils.fields.MonitorField(blank=True, default=django.utils.timezone.now, monitor='status', null=True, verbose_name='Proces starttidspunkt', when={'PROCESSING'}),
        ),
        migrations.AlterField(
            model_name='conversionqueueitem',
            name='status',
            field=model_utils.fields.StatusField(choices=[(0, 'dummy')], default='NEW', max_length=10, no_check_for_status=True, verbose_name='Status'),
        ),
        migrations.AlterField(
            model_name='location',
            name='scanner',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='locations', to='os2datascanner.scanner', verbose_name='Scan'),
        ),
        migrations.AlterModelOptions(
            name='scan',
            options={'ordering': ['-creation_time'], 'verbose_name': 'Report'},
        ),
        migrations.RemoveField(
            model_name='webversion',
            name='mime_type',
        ),
        migrations.AddField(
            model_name='version',
            name='mime_type',
            field=models.CharField(max_length=256, null=True, verbose_name='Content type'),
        ),
        migrations.AlterField(
            model_name='conversionqueueitem',
            name='url',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='os2datascanner.version', verbose_name='URL'),
        ),
        migrations.RemoveField(
            model_name='match',
            name='url',
        ),
        migrations.RemoveField(
            model_name='version',
            name='location',
        ),
        migrations.AddField(
            model_name='version',
            name='metadata',
            field=django.contrib.postgres.fields.jsonb.JSONField(blank=True, null=True),
        ),
        migrations.DeleteModel(
            name='RegexRule',
        ),
        migrations.CreateModel(
            name='Rule',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=256, unique=True, verbose_name='Navn')),
                ('description', models.TextField(verbose_name='Beskrivelse')),
                ('sensitivity', models.IntegerField(choices=[(0, 'Notifikation'), (1, 'Advarsel'), (2, 'Problem'), (3, 'Kritisk')], default=2, verbose_name='Følsomhed')),
                ('group', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='os2datascanner.group', verbose_name='Gruppe')),
                ('organization', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='os2datascanner.organization', verbose_name='Organisation')),
            ],
        ),
        migrations.RemoveField(
            model_name='scan',
            name='regex_rules',
        ),
        migrations.RemoveField(
            model_name='scanner',
            name='regex_rules',
        ),
        migrations.AddField(
            model_name='scanner',
            name='rules',
            field=models.ManyToManyField(blank=True, related_name='scanners', to='os2datascanner.Rule', verbose_name='Regler'),
        ),
        migrations.AlterModelOptions(
            name='regexpattern',
            options={'ordering': ('pk',)},
        ),
        migrations.CreateModel(
            name='RegexRule',
            fields=[
                ('rule_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='os2datascanner.rule')),
            ],
            bases=('os2datascanner.rule',),
        ),
        migrations.RemoveField(
            model_name='scan',
            name='do_address_scan',
        ),
        migrations.RemoveField(
            model_name='scan',
            name='do_name_scan',
        ),
        migrations.RemoveField(
            model_name='scanner',
            name='do_address_scan',
        ),
        migrations.RemoveField(
            model_name='scanner',
            name='do_name_scan',
        ),
        migrations.RemoveField(
            model_name='organization',
            name='address_blacklist',
        ),
        migrations.RemoveField(
            model_name='organization',
            name='address_whitelist',
        ),
        migrations.RemoveField(
            model_name='organization',
            name='cpr_whitelist',
        ),
        migrations.RemoveField(
            model_name='organization',
            name='name_blacklist',
        ),
        migrations.RemoveField(
            model_name='organization',
            name='name_whitelist',
        ),
        migrations.RemoveField(
            model_name='scan',
            name='blacklisted_addresses',
        ),
        migrations.RemoveField(
            model_name='scan',
            name='blacklisted_names',
        ),
        migrations.RemoveField(
            model_name='scan',
            name='whitelisted_addresses',
        ),
        migrations.RemoveField(
            model_name='scan',
            name='whitelisted_cprs',
        ),
        migrations.RemoveField(
            model_name='scan',
            name='whitelisted_names',
        ),
        migrations.CreateModel(
            name='AddressRule',
            fields=[
                ('rule_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='os2datascanner.rule')),
                ('database', models.IntegerField(choices=[(0, 'Post Danmarks liste over gadenavne pr. ca. 1. januar 2015')], default=0, verbose_name='Gadenavnedatabase')),
                ('blacklist', models.TextField(blank=True, default='', verbose_name='Sortlistede adresser')),
                ('whitelist', models.TextField(blank=True, default='', verbose_name='Godkendte adresser')),
            ],
            bases=('os2datascanner.rule',),
        ),
        migrations.CreateModel(
            name='CPRRule',
            fields=[
                ('rule_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='os2datascanner.rule')),
                ('do_modulus11', models.BooleanField(default=False, verbose_name='Tjek modulus-11')),
                ('ignore_irrelevant', models.BooleanField(default=False, verbose_name='Ignorer ugyldige fødselsdatoer')),
                ('whitelist', models.TextField(blank=True, default='', verbose_name='Godkendte CPR-numre')),
                ('examine_context', models.BooleanField(default=False, verbose_name='Tjek kontekst omkring match')),
            ],
            bases=('os2datascanner.rule',),
        ),
        migrations.CreateModel(
            name='NameRule',
            fields=[
                ('rule_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='os2datascanner.rule')),
                ('database', models.IntegerField(choices=[(0, 'Danmarks Statistiks liste over navne pr. 1. januar 2014')], default=0, verbose_name='Navnedatabase')),
                ('blacklist', models.TextField(blank=True, default='', verbose_name='Sortlistede navne')),
                ('whitelist', models.TextField(blank=True, default='', verbose_name='Godkendte navne')),
            ],
            bases=('os2datascanner.rule',),
        ),
        migrations.AlterField(
            model_name='statistic',
            name='relevant_size',
            field=models.BigIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='statistic',
            name='relevant_unsupported_size',
            field=models.BigIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='statistic',
            name='supported_size',
            field=models.BigIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='typestatistics',
            name='size',
            field=models.BigIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='scanner',
            name='e2_last_run_at',
            field=models.DateTimeField(null=True),
        ),
        migrations.AddField(
            model_name='exchangescanner',
            name='service_endpoint',
            field=models.URLField(max_length=256, null=True, verbose_name='Service endpoint'),
        ),
        migrations.RemoveField(
            model_name='exchangescanner',
            name='dir_to_scan',
        ),
        migrations.RemoveField(
            model_name='exchangescanner',
            name='is_exporting',
        ),
        migrations.RemoveField(
            model_name='exchangescanner',
            name='is_ready_to_scan',
        ),
        migrations.RemoveField(
            model_name='filescanner',
            name='mountpath',
        ),
        migrations.AlterField(
            model_name='match',
            name='sensitivity',
            field=models.IntegerField(choices=[(0, 'Grøn'), (1, 'Gul'), (2, 'Rød'), (3, 'Sort')], default=2, verbose_name='Følsomhed'),
        ),
        migrations.AlterField(
            model_name='match',
            name='sensitivity',
            field=models.IntegerField(choices=[(0, 'Notifikation'), (1, 'Advarsel'), (2, 'Problem'), (3, 'Kritisk')], default=2, verbose_name='Følsomhed'),
        ),
        migrations.DeleteModel(
            name='ConversionQueueItem',
        ),
        migrations.DeleteModel(
            name='Summary',
        ),
        migrations.DeleteModel(
            name='UrlLastModified',
        ),
        migrations.RemoveField(
            model_name='typestatistics',
            name='statistic',
        ),
        migrations.DeleteModel(
            name='Statistic',
        ),
        migrations.DeleteModel(
            name='TypeStatistics',
        ),
        migrations.DeleteModel(
            name='WebScan',
        ),
        migrations.RemoveField(
            model_name='webversion',
            name='referrers',
        ),
        migrations.DeleteModel(
            name='ReferrerUrl',
        ),
        migrations.DeleteModel(
            name='WebVersion',
        ),
        migrations.RemoveField(
            model_name='scan',
            name='recipients',
        ),
        migrations.RemoveField(
            model_name='scan',
            name='scanner',
        ),
        migrations.RemoveField(
            model_name='version',
            name='scan',
        ),
        migrations.DeleteModel(
            name='Location',
        ),
        migrations.DeleteModel(
            name='Match',
        ),
        migrations.DeleteModel(
            name='Scan',
        ),
        migrations.DeleteModel(
            name='Version',
        ),
        migrations.CreateModel(
            name='MSGraphMailScanner',
            fields=[
                ('scanner_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='os2datascanner.scanner')),
                ('tenant_id', models.CharField(max_length=256, verbose_name='Tenant ID')),
            ],
            options={
                'abstract': False,
            },
            bases=('os2datascanner.scanner',),
        ),
        migrations.CreateModel(
            name='DropboxScanner',
            fields=[
                ('scanner_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='os2datascanner.scanner')),
                ('token', models.CharField(max_length=64, null=True, validators=[django.core.validators.MinLengthValidator(64)], verbose_name='Token')),
            ],
            bases=('os2datascanner.scanner',),
        ),
        migrations.CreateModel(
            name='MSGraphFileScanner',
            fields=[
                ('scanner_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='os2datascanner.scanner')),
                ('tenant_id', models.CharField(max_length=256, verbose_name='Tenant ID')),
                ('scan_site_drives', models.BooleanField(default=True, verbose_name='Scan alle SharePoint-mapper')),
                ('scan_user_drives', models.BooleanField(default=True, verbose_name='Scan alle OneDrive-drev')),
            ],
            options={
                'abstract': False,
            },
            bases=('os2datascanner.scanner',),
        ),
        migrations.CreateModel(
            name='GoogleDriveScanner',
            fields=[
                ('scanner_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='os2datascanner.scanner')),
                ('service_account_file', models.FileField(upload_to='googledrive/serviceaccount/', validators=[os2datascanner.projects.admin.adminapp.models.scannerjobs.googledrivescanner.GoogleDriveScanner.validate_filetype_json])),
                ('user_emails', models.FileField(upload_to='googledrive/users/', validators=[os2datascanner.projects.admin.adminapp.models.scannerjobs.googledrivescanner.GoogleDriveScanner.validate_filetype_csv])),
            ],
            bases=('os2datascanner.scanner',),
        ),
        migrations.CreateModel(
            name='GmailScanner',
            fields=[
                ('scanner_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='os2datascanner.scanner')),
                ('service_account_file_gmail', models.FileField(upload_to='gmail/serviceaccount/', validators=[os2datascanner.projects.admin.adminapp.models.scannerjobs.gmail.GmailScanner.validate_filetype_json])),
                ('user_emails_gmail', models.FileField(upload_to='gmail/users/', validators=[os2datascanner.projects.admin.adminapp.models.scannerjobs.gmail.GmailScanner.validate_filetype_csv])),
            ],
            bases=('os2datascanner.scanner',),
        ),
        migrations.CreateModel(
            name='ScheduledCheckup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('handle_representation', django.contrib.postgres.fields.jsonb.JSONField(verbose_name='Reference')),
                ('interested_before', models.DateTimeField(null=True)),
                ('scanner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='checkups', to='os2datascanner.scanner', verbose_name='Tilknyttet scannerjob')),
            ],
        ),
        migrations.CreateModel(
            name='SbsysScanner',
            fields=[
                ('scanner_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='os2datascanner.scanner')),
            ],
            bases=('os2datascanner.scanner',),
        ),
        migrations.CreateModel(
            name='ScanStatus',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('scan_tag', django.contrib.postgres.fields.jsonb.JSONField(unique=True, verbose_name='Scan tag')),
                ('total_sources', models.IntegerField(null=True, verbose_name='Antal kilder')),
                ('explored_sources', models.IntegerField(null=True, verbose_name='Udforskede kilder')),
                ('total_objects', models.IntegerField(null=True, verbose_name='Antal objekter')),
                ('scanned_objects', models.IntegerField(null=True, verbose_name='Scannede objekter')),
                ('scanned_size', models.BigIntegerField(null=True, verbose_name='Størrelse af scannede objekter')),
                ('scanner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='statuses', to='os2datascanner.scanner', verbose_name='Tilknyttet scannerjob')),
            ],
            options={
                'verbose_name_plural': 'scan statuses',
            },
        ),
        migrations.AddField(
            model_name='organization',
            name='uuid',
            field=models.UUIDField(default=uuid.uuid4, editable=False, null=True),
        ),
    ]