# Part of the OSdatascanner system, copyright © 2014-2026 Magenta ApS.
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, you can
# obtain one at http://mozilla.org/MPL/2.0/.

import pytest

from django.core.management import call_command

from .test_utilities import create_reports_for
from ..reportapp.models.documentreport import DocumentReport


@pytest.mark.django_db
class TestDeleteScannerjobCommand:

    def test_delete_scannerjob(self, egon_sid_alias):
        # Arrange
        create_reports_for(egon_sid_alias, num=10, scanner_job_pk=51)
        create_reports_for(egon_sid_alias, num=10, scanner_job_pk=52)
        create_reports_for(egon_sid_alias, num=10, scanner_job_pk=53)

        # Act
        call_command("delete_scannerjob", 52)

        # Assert
        assert DocumentReport.objects.filter(scanner_job__scanner_pk=51).count() == 10
        assert DocumentReport.objects.filter(scanner_job__scanner_pk=52).count() == 0
        assert DocumentReport.objects.filter(scanner_job__scanner_pk=53).count() == 10
