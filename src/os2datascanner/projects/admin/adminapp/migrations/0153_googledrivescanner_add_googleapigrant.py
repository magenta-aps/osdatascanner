# Generated by Django 3.2.11 on 2025-03-18 14:57

from django.db import migrations, models
import django.db.models.deletion
import os2datascanner.projects.admin.adminapp.models.scannerjobs.googledrivescanner
import os2datascanner.projects.admin.adminapp.utils


class Migration(migrations.Migration):

    dependencies = [
        ('os2datascanner', '0152_gmailscanner_add_googleapigrant'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='googledrivescanner',
            name='service_account_file',
        ),
        migrations.RemoveField(
            model_name='googledrivescanner',
            name='user_emails',
        ),
        migrations.AddField(
            model_name='googledrivescanner',
            name='google_api_grant',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='grants.googleapigrant'),
        ),
        migrations.AddField(
            model_name='googledrivescanner',
            name='user_emails_gmail',
            field=models.FileField(blank=True, null=True, upload_to=os2datascanner.projects.admin.adminapp.utils.upload_path_gdrive_users, validators=[os2datascanner.projects.admin.adminapp.models.scannerjobs.googledrivescanner.GoogleDriveScanner.validate_filetype_csv]),
        ),
    ]
