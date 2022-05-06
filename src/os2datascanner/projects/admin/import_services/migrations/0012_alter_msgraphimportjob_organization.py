# Generated by Django 3.2.11 on 2022-04-11 14:17

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('organizations', '0006_auto_20211014_0300'),
        ('import_services', '0011_auto_20220405_0903'),
    ]

    operations = [
        migrations.AlterField(
            model_name='msgraphimportjob',
            name='organization',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='msimport', to='organizations.organization', verbose_name='organization'),
        ),
    ]