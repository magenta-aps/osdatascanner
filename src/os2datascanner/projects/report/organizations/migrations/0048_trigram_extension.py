from django.contrib.postgres.operations import TrigramExtension
from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('organizations', '0047_alter_account_unique_together'),
    ]

    operations = [
        TrigramExtension()
    ]