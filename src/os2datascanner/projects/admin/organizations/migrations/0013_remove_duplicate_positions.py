# Generated by Django 3.2.11 on 2023-01-05 07:52

from django.db import migrations, models
from django.db.models import Count


def remove_duplicate_positions(apps, schema_editor):
    Position = apps.get_model("organizations", "Position")

    duplicates = Position.objects.values("account", "unit", "role").annotate(count=Count("pk")).filter(count__gt=1)

    for position in duplicates:
        positions = Position.objects.filter(account=position.get("account"), unit=position.get("unit"), role=position.get("role"))

        to_keep = positions.first()
        positions.exclude(pk=to_keep.pk).delete()



class Migration(migrations.Migration):

    dependencies = [
        ('organizations', '0012_alter_position_unit'),
    ]

    operations = [
        migrations.RunPython(
            remove_duplicate_positions, reverse_code=migrations.RunPython.noop
        )
    ]
