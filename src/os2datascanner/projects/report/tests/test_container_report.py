# src/os2datascanner/projects/report/tests/test_container_report.py
# Part of the OSdatascanner system, copyright © 2014-2026 Magenta ApS.
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, you can
# obtain one at http://mozilla.org/MPL/2.0/.

import pytest
from django.db import IntegrityError

from ..reportapp.models.container_report import ContainerReport
from ..reportapp.models.documentreport import DocumentReport
from .test_utilities import create_reports_for


@pytest.mark.django_db
class TestContainerReport:
    def test_unique_on_scanner_job_and_path(self, scanner_job):
        ContainerReport.objects.create(
                scanner_job=scanner_job, path="case-path", source_type="sbsys-db")
        with pytest.raises(IntegrityError):
            ContainerReport.objects.create(
                    scanner_job=scanner_job, path="case-path", source_type="sbsys-db")

    def test_document_report_can_be_linked_to_a_container(self, scanner_job, egon_email_alias):
        create_reports_for(egon_email_alias, num=1)
        dr = DocumentReport.objects.get()
        container = ContainerReport.objects.create(
                scanner_job=scanner_job, path="case-path", source_type="sbsys-db")

        dr.container = container
        dr.save(update_fields=["container"])
        dr.refresh_from_db()

        assert dr.container == container
        assert container.document_reports.get() == dr

    def test_deleting_container_does_not_delete_document_report(
            self, scanner_job, egon_email_alias):
        create_reports_for(egon_email_alias, num=1)
        dr = DocumentReport.objects.get()
        container = ContainerReport.objects.create(
                scanner_job=scanner_job, path="case-path", source_type="sbsys-db")
        dr.container = container
        dr.save(update_fields=["container"])

        container.delete()
        dr.refresh_from_db()

        assert dr.container is None
