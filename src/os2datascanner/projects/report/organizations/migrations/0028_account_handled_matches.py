# Generated by Django 3.2.11 on 2023-10-13 13:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('organizations', '0027_organization_msgraph_write_permissions'),
    ]

    operations = [
        migrations.AddField(
            model_name='account',
            name='handled_matches',
            field=models.IntegerField(blank=True, default=0, null=True, verbose_name='Number of handled matches'),
        ),
    ]
