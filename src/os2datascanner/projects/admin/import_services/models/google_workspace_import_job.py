from django.db import models
from django.utils.translation import gettext_lazy as _

from ...core.models.background_job import BackgroundJob
from .....utils.system_utilities import time_now

import structlog
logger = structlog.get_logger(__name__)


class GoogleWorkspaceImportJob(BackgroundJob):

    organization = models.ForeignKey(
        'organizations.Organization',
        on_delete=models.CASCADE,
        verbose_name=_('organization'),
        related_name='googleworkspaceimportjobs'
    )

    grant = models.ForeignKey(
        'grants.GoogleApiGrant',
        on_delete=models.SET_NULL,
        verbose_name=_("Google API Grant"),
        null=True,
        blank=True,
    )

    delegated_admin_email = models.EmailField(
        verbose_name=_('Delegated admin email used for this run')
    )

    def __str__(self):
        return f"Google Workspace import for {self.organization}"

    def job_label(self) -> str:
        return "Google Workspace import job"

    def _fetch_and_map_ous(self, client):  # noqa Cognitive complexity is too high
        """Fetch OUs from Google and map to model instances."""

        from ...organizations.models import OrganizationalUnit

        self.status = "Fetching organizational units..."
        self.save(update_fields=["status"])

        # Fetch directly from client
        raw_ous = list(client.list_organizational_units())
        logger.info("Fetched OUs from Google Workspace", count=len(raw_ous))

        # Map inline - no separate function
        now = time_now()
        to_add = []
        to_update = []
        ou_map = {}
        imported_ids = set()
        parent_map = {}

        # Build index
        ou_index = {ou['orgUnitId']: ou for ou in raw_ous}
        imported_id_list = [f"google-ou:{ou['orgUnitId']}" for ou in raw_ous]
        imported_ids.update(imported_id_list)

        # Bulk fetch existing
        existing_ous = OrganizationalUnit.objects.filter(
            organization=self.organization,
            imported_id__in=imported_id_list
        )
        existing_by_imported_id = {ou.imported_id: ou for ou in existing_ous}

        # Process each OU
        for ou_data in raw_ous:
            raw_id = ou_data["orgUnitId"]
            imported_id = f"google-ou:{raw_id}"
            name = ou_data.get("name") or ou_data["orgUnitPath"].split("/")[-1]

            if not ou_data.get("parentOrgUnitId") and not name:
                name = self.organization.name or "Root"

            existing = existing_by_imported_id.get(imported_id)

            if existing:
                if existing.name != name:
                    existing.name = name
                    to_update.append((existing, ("name",)))
                ou_map[imported_id] = existing
            else:
                org_unit = OrganizationalUnit(
                    imported_id=imported_id,
                    organization=self.organization,
                    name=name,
                    imported=True,
                    last_import=now,
                    last_import_requested=now,
                    lft=0, rght=0, tree_id=0, level=0,
                )
                to_add.append(org_unit)
                ou_map[imported_id] = org_unit

            # Track parent relationships
            parent_raw_id = ou_data.get("parentOrgUnitId")
            if parent_raw_id and parent_raw_id in ou_index:
                parent_map[imported_id] = f"google-ou:{parent_raw_id}"
            else:
                parent_map[imported_id] = None

        logger.info("Mapped OUs", total=len(ou_map), new=len(to_add), updated=len(to_update))
        return (to_add, to_update, ou_map, imported_ids, parent_map), raw_ous
