# Generated by Django 3.2.11 on 2024-01-08 09:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('organizations', '0028_add_account_full_name_search_vector_index'),
    ]

    operations = [
        migrations.AddField(
            model_name='organization',
            name='email_header_banner',
            field=models.ImageField(blank=True, null=True, upload_to='', verbose_name='Email header banner'),
        ),
    ]
