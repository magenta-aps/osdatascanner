from django.contrib.postgres.operations import TrigramExtension
from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('organizations', '0048_organizationalunit_hidden'),
    ]

    operations = [
        TrigramExtension()
    ]