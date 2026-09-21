# Part of the OSdatascanner system, copyright © 2014-2026 Magenta ApS.
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, you can
# obtain one at http://mozilla.org/MPL/2.0/.

from django.db import models

from .scanner_reference import ScannerReference


class ContainerReport(models.Model):
    """A grouping anchor for DocumentReports that belong to the same logical
    container (initially: an SBSYS case). Carries no resolution state of its
    own -- whether a container counts as "handled" is always derived from
    its children, never stored here."""

    path = models.CharField(max_length=256)

    scanner_job = models.ForeignKey(
        ScannerReference,
        on_delete=models.CASCADE,
        related_name='container_reports',
    )

    source_type = models.CharField(max_length=2000, db_index=True)

    created_timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["scanner_job", "path"],
                name="unique_container_scanner_pk_and_path")
        ]

    def __str__(self):
        return f"<ContainerReport: {self.path} ({self.scanner_job})>"
