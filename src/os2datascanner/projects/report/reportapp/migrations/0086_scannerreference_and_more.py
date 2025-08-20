import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('organizations', '0061_organization_leadertab_config'),
        ('os2datascanner_report', '0085_documentreport_relevance'),
    ]

    operations = [
        migrations.CreateModel(
            name='ScannerReference',
            fields=[
                ('scanner_pk', models.IntegerField(primary_key=True, serialize=False)),
                ('scanner_name', models.CharField(max_length=256, null=True)),
            ],
        ),
        migrations.AddField(
            model_name='documentreport',
            name='scanner_job',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='document_reports', to='os2datascanner_report.scannerreference'),
        ),
        migrations.AddField(
            model_name='scannerreference',
            name='organization',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='scanners', to='organizations.organization'),
        ),
    ]
