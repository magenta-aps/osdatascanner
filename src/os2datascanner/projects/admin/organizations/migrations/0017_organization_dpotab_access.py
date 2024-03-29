# Generated by Django 3.2.11 on 2023-08-25 09:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('organizations', '0016_organization_leadertab_access'),
    ]

    operations = [
        migrations.AddField(
            model_name='organization',
            name='dpotab_access',
            field=models.CharField(choices=[('M', 'Managers'), ('D', 'Data Protection Officers'), ('S', 'Superusers'), ('N', 'None')], default='D', max_length=1),
        ),
        migrations.AlterField(
            model_name='organization',
            name='leadertab_access',
            field=models.CharField(choices=[('M', 'Managers'), ('D', 'Data Protection Officers'), ('S', 'Superusers'), ('N', 'None')], default='M', max_length=1),
        ),
    ]
