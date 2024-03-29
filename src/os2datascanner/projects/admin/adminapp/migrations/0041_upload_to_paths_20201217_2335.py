# Generated by Django 2.2.10 on 2020-12-18 05:35

from django.db import migrations, models
import os2datascanner.projects.admin.adminapp.models.scannerjobs.gmail
import os2datascanner.projects.admin.adminapp.models.scannerjobs.googledrivescanner
import os2datascanner.projects.admin.adminapp.utils
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('os2datascanner', '0040_remove_uuid_null'),
    ]

    operations = [
        migrations.AlterField(
            model_name='exchangescanner',
            name='userlist',
            field=models.FileField(upload_to=os2datascanner.projects.admin.adminapp.utils.upload_path_exchange_users),
        ),
        migrations.AlterField(
            model_name='gmailscanner',
            name='service_account_file_gmail',
            field=models.FileField(upload_to=os2datascanner.projects.admin.adminapp.utils.upload_path_gmail_service_account, validators=[os2datascanner.projects.admin.adminapp.models.scannerjobs.gmail.GmailScanner.validate_filetype_json]),
        ),
        migrations.AlterField(
            model_name='gmailscanner',
            name='user_emails_gmail',
            field=models.FileField(upload_to=os2datascanner.projects.admin.adminapp.utils.upload_path_gmail_users, validators=[os2datascanner.projects.admin.adminapp.models.scannerjobs.gmail.GmailScanner.validate_filetype_csv]),
        ),
        migrations.AlterField(
            model_name='googledrivescanner',
            name='service_account_file',
            field=models.FileField(upload_to=os2datascanner.projects.admin.adminapp.utils.upload_path_gdrive_service_account, validators=[os2datascanner.projects.admin.adminapp.models.scannerjobs.googledrivescanner.GoogleDriveScanner.validate_filetype_json]),
        ),
        migrations.AlterField(
            model_name='googledrivescanner',
            name='user_emails',
            field=models.FileField(upload_to=os2datascanner.projects.admin.adminapp.utils.upload_path_gdrive_users, validators=[os2datascanner.projects.admin.adminapp.models.scannerjobs.googledrivescanner.GoogleDriveScanner.validate_filetype_csv]),
        ),
        migrations.AlterField(
            model_name='webscanner',
            name='sitemap',
            field=models.FileField(blank=True, upload_to=os2datascanner.projects.admin.adminapp.utils.upload_path_webscan_sitemap, verbose_name='Sitemap Fil'),
        ),
    ]



