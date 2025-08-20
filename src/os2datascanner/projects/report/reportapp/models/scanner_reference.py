from django.db import models

from os2datascanner.projects.report.organizations.models.organization import Organization
from os2datascanner.projects.report.organizations.models.organizational_unit import OrganizationalUnit  # noqa


class ScannerReference(models.Model):
    scanner_pk = models.IntegerField(
        primary_key=True
    )
    scanner_name = models.CharField(
        max_length=256,
        null=True,
    )
    organization = models.ForeignKey(
        Organization,
        on_delete=models.SET_NULL,
        related_name='scanners',
        default=None,
        null=True,
    )
    org_units = models.ManyToManyField(
        OrganizationalUnit,
        related_name='scanners',
    )
    scan_entire_org = models.BooleanField(
        default=False,
    )
    only_notify_superadmin = models.BooleanField(
        default=False,
    )

    def __str__(self):
        return self.scanner_name or f"Unnamed scanner ({self.scanner_pk})"
