# Generated by Django 3.2.11 on 2023-01-06 07:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('organizations', '0012_remove_duplicate_positions'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='position',
            constraint=models.UniqueConstraint(fields=('account', 'unit', 'role'), name='organizations_position_unique_constraint'),
        ),
    ]