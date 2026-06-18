# Part of the OSdatascanner system, copyright © 2014-2026 Magenta ApS.
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, you can
# obtain one at http://mozilla.org/MPL/2.0/.

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0010_client_import_source'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='client',
            name='features',
        ),
    ]
