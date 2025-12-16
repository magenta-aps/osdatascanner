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

    def _fetch_and_map_users(self, client):
        """Fetch users from Google and map to model instances."""
        from ...organizations.models import Account

        self.status = "Fetching users..."
        self.save(update_fields=["status"])

        # Fetch directly
        raw_users = list(client.list_users())

        # Map inline
        to_create = []
        to_update = []
        account_map = {}
        all_imported_ids = set()

        # Bulk fetch existing accounts
        primaries = [u["primaryEmail"] for u in raw_users if u.get("primaryEmail")]
        existing_accounts = Account.objects.filter(
            organization=self.organization,
            username__in=primaries,
        )
        existing_by_username = {acc.username: acc for acc in existing_accounts}

        # Process each user
        for user in raw_users:
            primary = user.get("primaryEmail")
            if not primary:
                continue

            given_name = user.get("name", {}).get("givenName", "")
            family_name = user.get("name", {}).get("familyName", "")
            imported_id = f"google-user:{primary}"

            existing = existing_by_username.get(primary)
            if existing:
                existing.email = primary
                existing.first_name = given_name or ""
                existing.last_name = family_name or ""
                existing.imported = True
                existing.imported_id = imported_id
                existing.last_import = time_now()
                existing.last_import_requested = time_now()

                to_update.append((existing, ['email', 'first_name', 'last_name',
                                             'imported', 'imported_id',
                                             'last_import', 'last_import_requested']))
                account_map[primary] = existing
            else:
                acc_obj = Account(
                    username=primary,
                    email=primary,
                    first_name=given_name or "",
                    last_name=family_name or "",
                    organization=self.organization,
                    imported_id=imported_id,
                    imported=True,
                )
                to_create.append(acc_obj)
                account_map[primary] = acc_obj

            all_imported_ids.add(imported_id)

        return (to_create, to_update, account_map, all_imported_ids), raw_users

    def _create_user_aliases(self, users, account_map):
        from ...organizations.models.aliases import Alias, AliasType

        aliases = []
        imported_ids = set()

        for user in users:
            primary = user.get("primaryEmail")
            if not primary:
                continue

            account = account_map.get(primary)
            if not account:
                continue

            for alias_email in user.get("aliases", []):
                if not alias_email:
                    continue

                imported_id = f"google-alias:{primary}:{alias_email}"

                alias = Alias(
                    account=account,
                    _alias_type=AliasType.EMAIL,
                    _value=alias_email,
                    imported_id=imported_id,
                )
                aliases.append(alias)
                imported_ids.add(imported_id)

        return aliases, imported_ids

    def _create_ou_positions(self, users, account_map, ou_map):
        from ...organizations.models import Position

        positions = []
        imported_ids = set()

        for user in users:
            primary = user.get("primaryEmail")
            if not primary:
                continue

            account = account_map.get(primary)
            if not account:
                continue

            ou_path = user.get("orgUnitPath")
            if not ou_path:
                continue

            # Find OU via path
            for imported_id, ou in ou_map.items():
                if getattr(ou, "path", None) == ou_path:
                    pos_imported_id = f"google-position:{primary}:{imported_id}"

                    pos = Position(
                        account=account,
                        unit=ou,
                        imported_id=pos_imported_id,
                    )
                    positions.append(pos)
                    imported_ids.add(pos_imported_id)
                    break

        return positions, imported_ids
