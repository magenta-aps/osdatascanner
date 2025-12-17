from django.db import models
from django.utils.translation import gettext_lazy as _

from .....utils.section import suppress_django_signals
from ..google_workspace_client import GoogleWorkspaceClient
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

    @suppress_django_signals
    def run(self):
        """
        Performs the complete Google Workspace import.
        Imports organizational units, users, positions, and aliases.
        """
        from ...organizations.models.organizational_unit import OrganizationalUnit
        from ...organizations.models import Account

        # Initialize and authenticate
        self.status = "Authenticating with Google Workspace..."
        self.save(update_fields=["status"])
        client = self._initialize_client()
        try:
            # Fetch and map OUs
            (ou_to_add, ou_to_update, ou_map, ou_imported_ids, parent_map), raw_ous = \
                self._fetch_and_map_ous(client)

            # Fetch and map users
            (new_users, users_to_update, account_map, user_imported_ids), raw_users = \
                self._fetch_and_map_users(client)
        except Exception as e:
            logger.error(
                "Google Workspace import failed during fetch phase",
                organization=str(self.organization),
                error=str(e),
            )
            self.status = "Import failed while fetching data from Google"
            self.save(update_fields=["status"])
            raise

        # Combine all imported IDs
        all_imported_ids = ou_imported_ids | user_imported_ids

        # PHASE 1: Save OUs and users (without OU parent relationships)
        self.status = "Saving organizational units and users..."
        self.save(update_fields=["status"])

        self._save_core_entities(
            ou_to_add, ou_to_update,
            new_users, users_to_update,
            all_imported_ids
        )

        # Rebuild MPTT tree after creating OUs
        OrganizationalUnit.objects.rebuild()

        # PHASE 2: Set OU parent relationships + save positions and aliases
        self.status = "Processing relationships and memberships..."
        self.save(update_fields=["status"])

        # Refresh maps from database (now all have PKs)
        saved_ous = OrganizationalUnit.objects.filter(
            organization=self.organization,
            imported_id__in=list(ou_map.keys())
        )
        ou_map = {ou.imported_id: ou for ou in saved_ous}

        saved_usernames = list(account_map.keys())
        saved_accounts = Account.objects.filter(
            organization=self.organization,
            username__in=saved_usernames
        )
        account_map = {acc.username: acc for acc in saved_accounts}

        # Combine phase 2 + 3 into ONE prepare_and_publish call
        position_stats = self._set_relationships_and_save_positions_aliases(
            parent_map, raw_users, account_map, ou_map, raw_ous, all_imported_ids
        )

        self.status = "Import complete."
        self.save(update_fields=["status"])

        return {
            "ous": len(ou_imported_ids),
            "users": len(new_users) + len(users_to_update),
            **position_stats,
        }

    def _initialize_client(self):
        """Initialize and authenticate the Google Workspace client."""
        service_account_info = getattr(self.grant, "service_account_dict", None)
        if not service_account_info:
            raise ValueError("GoogleApiGrant.service_account is missing or invalid.")

        if not self.delegated_admin_email:
            raise ValueError("Delegated admin email is required but not provided.")

        client = GoogleWorkspaceClient(
            service_account_info=service_account_info,
            admin_email=self.delegated_admin_email
        )
        client.authenticate()
        return client

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
            if parent_raw_id:
                parent_imported_id = f"google-ou:{parent_raw_id}"
                parent_map[imported_id] = parent_imported_id
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

    def _save_core_entities(self, ou_to_add, ou_to_update,
                            new_users, users_to_update, all_imported_ids):
        """
        Phase 1: Save OUs and users using prepare_and_publish.
        OU parent relationships are NOT set yet.
        """
        from ...organizations.utils import prepare_and_publish

        logger.info("Phase 1: Saving new entities",
                    ous=len(ou_to_add), users=len(new_users))
        logger.info("Phase 1: Updating entities",
                    ous=len(ou_to_update), users=len(users_to_update))

        # Combine all entities for prepare_and_publish
        to_add = ou_to_add + new_users
        to_update = ou_to_update + users_to_update

        prepare_and_publish(
            org=self.organization,
            all_uuids=all_imported_ids,
            to_add=to_add,
            to_update=to_update,
            to_delete=[],
        )

    def _set_relationships_and_save_positions_aliases(self, parent_map, raw_users, account_map, ou_map, raw_ous, all_imported_ids):  # noqa - Cognitive complexity is too high
        """
        Phase 2 (combined): Set OU parent relationships AND save positions/aliases.
        This reduces message count by combining operations into ONE prepare_and_publish call.
        """
        from ...organizations.models.organizational_unit import OrganizationalUnit
        from ...organizations.models import Position, Alias
        from ...organizations.utils import prepare_and_publish

        # Part 1: Prepare OU parent updates
        all_ou_ids = set(parent_map.keys())
        all_ou_ids.update(v for v in parent_map.values() if v is not None)

        saved_ous = OrganizationalUnit.objects.filter(
            organization=self.organization,
            imported_id__in=all_ou_ids
        )
        ou_map_for_parents = {ou.imported_id: ou for ou in saved_ous}

        logger.info("Phase 2: Processing parent relationships",
                    ous_found=len(ou_map_for_parents), relationships=len(parent_map))

        ous_to_update = []
        for child_id, parent_id in parent_map.items():
            child = ou_map_for_parents.get(child_id)
            if not child:
                logger.warning("Child OU not in database", child_id=child_id)
                continue

            if parent_id is None:
                if child.parent is not None:
                    child.parent = None
                    ous_to_update.append((child, ("parent",)))
            else:
                parent = ou_map_for_parents.get(parent_id)
                if parent:
                    if child.parent != parent:
                        child.parent = parent
                        ous_to_update.append((child, ("parent",)))
                else:
                    if child.parent is not None:
                        child.parent = None
                        ous_to_update.append((child, ("parent",)))
                        logger.warning("Parent not found, setting as root",
                                       child=child.name, parent_id=parent_id)

        # Part 2: Create positions and aliases
        self.status = "Processing positions and aliases..."
        self.save(update_fields=["status"])

        user_aliases, alias_imported_ids = self._create_user_aliases(raw_users, account_map)
        ou_positions, position_imported_ids = self._create_ou_positions(
            raw_users, account_map, ou_map, raw_ous
        )

        # Update all_imported_ids
        all_imported_ids = all_imported_ids | position_imported_ids | alias_imported_ids

        # Fetch existing positions/aliases
        all_position_ids = [p.imported_id for p in ou_positions]
        all_alias_ids = [a.imported_id for a in user_aliases]

        existing_positions = Position.objects.filter(
            account__organization=self.organization,
            imported_id__in=all_position_ids
        )
        existing_aliases = Alias.objects.filter(
            account__organization=self.organization,
            imported_id__in=all_alias_ids
        )

        existing_position_map = {p.imported_id: p for p in existing_positions}
        existing_alias_map = {a.imported_id: a for a in existing_aliases}

        # Split positions/aliases into new vs update
        new_positions = [
            p for p in ou_positions
            if p.imported_id not in existing_position_map
        ]
        positions_to_update = [
            (existing_position_map[p.imported_id], ("unit", "account"))
            for p in ou_positions
            if p.imported_id in existing_position_map
        ]

        new_aliases = [
            a for a in user_aliases
            if a.imported_id not in existing_alias_map
        ]
        aliases_to_update = [
            (existing_alias_map[a.imported_id], ("_value", "_alias_type"))
            for a in user_aliases
            if a.imported_id in existing_alias_map
        ]

        # Combine ALL updates into ONE prepare_and_publish call
        logger.info("Phase 2 (combined): Saving all updates",
                    ou_parents=len(ous_to_update),
                    new_positions=len(new_positions),
                    updated_positions=len(positions_to_update),
                    new_aliases=len(new_aliases),
                    updated_aliases=len(aliases_to_update))

        prepare_and_publish(
            org=self.organization,
            all_uuids=all_imported_ids,
            to_add=new_positions + new_aliases,
            to_update=ous_to_update + positions_to_update + aliases_to_update,
            to_delete=[],
        )

        # Rebuild MPTT after parent updates
        OrganizationalUnit.objects.rebuild()

        return {
            "ou_positions": len(ou_positions),
            "aliases": len(user_aliases),
        }

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

    def _create_ou_positions(self, users, account_map, ou_map, raw_ous):
        from ...organizations.models import Position

        positions = []
        imported_ids = set()

        path_to_id = {
            ou['orgUnitPath']: ou['orgUnitId']
            for ou in raw_ous
            if ou.get('orgUnitPath') and ou.get('orgUnitId')
        }

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

            ou_id = path_to_id.get(ou_path)
            if not ou_id:
                continue

            ou_imported_id = f"google-ou:{ou_id}"
            ou_obj = ou_map.get(ou_imported_id)
            if not ou_obj:
                continue

            # Find OU via path
            pos_imported_id = f"google-position:{primary}:{ou_id}"

            pos = Position(
                account=account,
                unit=ou_obj,
                imported_id=pos_imported_id,
            )
            positions.append(pos)
            imported_ids.add(pos_imported_id)

        return positions, imported_ids
