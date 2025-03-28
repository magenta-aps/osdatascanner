# Generated by Django 3.2.11 on 2025-02-25 14:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_queue_definitions'),
    ]

    operations = [
        migrations.AlterField(
            model_name='backgroundjob',
            name='_exec_state',
            field=models.CharField(choices=[('waiting', 'Afventer'), ('running', 'Kører'), ('cancelling', 'Annullering i gang'), ('finished', 'Afsluttet'), ('cancelled', 'Annulleret'), ('failed', 'Fejlet'), ('finished with warnings', 'Afsluttet med advarsler')], default='waiting', max_length=30, verbose_name='execution state'),
        ),
    ]
