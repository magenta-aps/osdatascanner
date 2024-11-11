from django.contrib.postgres.operations import TrigramExtension
from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('organizations', '0047_account_username_org_constraint_and_verbose_names'),
    ]

    operations = [
        TrigramExtension()
    ]