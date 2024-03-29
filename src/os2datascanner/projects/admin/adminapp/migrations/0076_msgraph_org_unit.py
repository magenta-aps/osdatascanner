# Generated by Django 3.2.11 on 2022-04-11 09:53

from django.db import migrations
import mptt.fields


class Migration(migrations.Migration):

    dependencies = [
        ('organizations', '0006_auto_20211014_0300'),
        ('os2datascanner', '0075_msgraphcalendarscanner'),
    ]

    operations = [
        migrations.AddField(
            model_name='msgraphcalendarscanner',
            name='org_unit',
            field=mptt.fields.TreeManyToManyField(blank=True, related_name='msgraphcalendarscanners', to='organizations.OrganizationalUnit', verbose_name='organizational unit'),
        ),
        migrations.AddField(
            model_name='msgraphfilescanner',
            name='org_unit',
            field=mptt.fields.TreeManyToManyField(blank=True, related_name='msgraphfilescanners', to='organizations.OrganizationalUnit', verbose_name='organizational unit'),
        ),
        migrations.AddField(
            model_name='msgraphmailscanner',
            name='org_unit',
            field=mptt.fields.TreeManyToManyField(blank=True, related_name='msgraphmailscanners', to='organizations.OrganizationalUnit', verbose_name='organizational unit'),
        ),
    ]
