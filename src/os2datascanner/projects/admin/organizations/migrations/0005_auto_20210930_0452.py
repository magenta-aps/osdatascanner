# Generated by Django 3.2.4 on 2021-09-30 09:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('organizations', '0004_alter_field_imported_id_from_charfield_to_textfield'),
    ]

    operations = [
        migrations.AlterField(
            model_name='alias',
            name='_alias_type',
            field=models.CharField(choices=[('SID', 'SID'), ('email', 'Email'), ('generic', 'Generic')], db_column='alias_type', db_index=True, max_length=32, verbose_name='alias type'),
        ),
        migrations.AlterField(
            model_name='position',
            name='role',
            field=models.CharField(choices=[('employee', 'Employee'), ('manager', 'Manager'), ('dpo', 'Data protection officer')], db_index=True, default='employee', max_length=30),
        ),
    ]



