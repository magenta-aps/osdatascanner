from enum import Enum
from typing import Any, Mapping, Sequence

import structlog
from more_itertools import first, one

from .keycloak_actions import _dummy_pc

from .models import (Account, Alias, Position,
                     Organization, OrganizationalUnit)
from .models.aliases import AliasType
from os2datascanner.utils.system_utilities import time_now
from .utils import prepare_and_publish
from os2datascanner.utils.section import suppress_django_signals

logger = structlog.get_logger("admin_organizations")

# TODO: Place somewhere reusable, or find a smarter way to ID aliases imported_id..
EMAIL_ALIAS_IMPORTED_ID_SUFFIX = "/email"


class Role(Enum):
    EMPLOYEE = "employee"
    MANAGER = "manager"


ImportedID = str


@suppress_django_signals
def perform_os2mo_import(org_unit_list: list,  # noqa: CCR001, C901 too high cognitive complexity
                         organization: Organization,
                         progress_callback=_dummy_pc):
    accounts: Mapping[ImportedID, Account] = {}
    aliases: Mapping[ImportedID, Alias] = {}
    account_employee_positions: Mapping[
            Account, Sequence[OrganizationalUnit]] = {}
    account_manager_positions: Mapping[
            Account, Sequence[OrganizationalUnit]] = {}
    ous: Mapping[ImportedID, OrganizationalUnit] = {}
    ou_parent_relations: Mapping[OrganizationalUnit, ImportedID] = {}

    now = time_now()

    to_add = []
    position_hashes = set()

    to_update = []
    to_delete = []

    # Set to contain retrieved uuids - things we have locally but aren't present remotely
    # will be deleted.
    all_uuids = set()
    progress_callback("org_unit_count", len(org_unit_list))

    def evaluate_org_unit(
            unit_raw: dict[str, Any]) -> (OrganizationalUnit, dict[str, str]):
        """ Evaluates given dictionary (which should be of one ou), decides if corresponding
        local object (if any) is to be updated, a new one is to be created or no actions.
        Returns an OrganizationalUnit object."""
        unit_imported_id = unit_raw.get("uuid")
        unit_name = unit_raw.get("name")

        try:
            org_unit = OrganizationalUnit.objects.get(
                organization=organization, imported_id=unit_imported_id)

            if org_unit.name != unit_name:
                org_unit.name = unit_name
                to_update.append((org_unit, ("name",)))

            # Don't do anything with parent_id at this point -- that's an
            # imported ID and we need a database primary key. We handle that
            # just before we submit changes for execution

        except OrganizationalUnit.DoesNotExist:
            org_unit = OrganizationalUnit(
                imported_id=unit_imported_id,
                organization=organization,
                hidden=organization.importservice.hide_units_on_import,
                name=unit_name,
                imported=True,
                last_import=now,
                last_import_requested=now,
                lft=0, rght=0, tree_id=0, level=0
            )
            to_add.append(org_unit)

        ous[unit_imported_id] = org_unit
        all_uuids.add(unit_imported_id)
        return org_unit, unit_raw.get("parent")

    def evaluate_unit_member(member: dict) -> Account | None:
        imported_id = member.get("uuid")
        username = member.get("user_key", None)
        first_name = member.get("given_name", "")
        last_name = member.get("surname", "")
        email = get_email_address(member)

        if not username:
            logger.info(f'Object not a user or empty user key for user: {member}')
            return None

        account = accounts.get(imported_id)
        if account is None:
            try:
                account = Account.objects.get(
                    organization=organization, imported_id=imported_id)
                for attr_name, expected in (
                        ("username", username),
                        ("first_name", first_name),
                        ("last_name", last_name),
                        ("email", email),
                ):
                    if getattr(account, attr_name) != expected:
                        setattr(account, attr_name, expected)
                        to_update.append((account, (attr_name,)))

            except Account.DoesNotExist:
                account = Account(
                    imported_id=imported_id,
                    organization=organization,
                    username=username,
                    first_name=first_name,
                    last_name=last_name,
                    email=email,
                )
                to_add.append(account)
                accounts[imported_id] = account

            all_uuids.add(imported_id)
        return account

    def evaluate_aliases(account: Account, email: str):
        imported_id = f"{account.imported_id}{EMAIL_ALIAS_IMPORTED_ID_SUFFIX}"
        alias = aliases.get(imported_id)
        if alias is None:
            try:
                alias = Alias.objects.get(
                    imported_id=imported_id,
                    account=account,
                    _alias_type=AliasType.EMAIL.value)
                for attr_name, expected in (("_value", email),):
                    if getattr(alias, attr_name) != expected:
                        setattr(alias, attr_name, expected)
                        to_update.append((alias, (attr_name,)))

            except Alias.DoesNotExist:
                alias = Alias(
                    imported_id=imported_id,
                    account=account,
                    _alias_type=AliasType.EMAIL.value,
                    _value=email
                )
                to_add.append(alias)
            aliases[imported_id] = alias
            all_uuids.add(imported_id)

    def get_email_address(obj: dict[str, Any]) -> str:
        """
        Get the email address from an employee or manager object.

        Args:
            obj: the GraphQL object containing the person, i.e. an employee
                 object or a manager object.

        Returns:
            Email address or the empty string if no email address is found
        """

        email = first(obj.get("addresses"), dict()).get("name", "")
        if not email:
            logger.info(f'No email in: {obj}')
        return email

    def positions_to_add(acc: Account, unit: OrganizationalUnit, role: Role):
        """ Helper function that appends positions to to_add if not present locally """
        try:
            Position.objects.get(account=acc, unit=unit, role=role.value, imported=True)
        except Position.DoesNotExist:
            position = Position(
                imported=True,
                account=acc,
                unit=unit,
                role=role.value,)
            position_hash = hash(str(acc.uuid) + str(unit.uuid) + role.value)

            # There's a chance we've already added this position to the list,
            # due to how the data we receive looks.
            if position_hash not in position_hashes:
                to_add.append(position)
                position_hashes.add(position_hash)

        # TODO: Comment above also means we're potentially appending the same unit n times,
        # which has no functionality breaking consequences, but is waste of space.
        if role == Role.EMPLOYEE:
            account_employee_positions.setdefault(acc, []).append(unit)
        if role == Role.MANAGER:
            account_manager_positions.setdefault(acc, []).append(unit)

    def positions_to_delete():
        """Helper function that figures out which position objects are to be deleted.
        Adds positions to to_delete list.
        Returns nothing."""
        for empl_acc, units in account_employee_positions.items():
            employee_positions_to_delete = Position.employees.filter(
                account=empl_acc, imported=True).exclude(unit__in=units)
            if employee_positions_to_delete:
                to_delete.append(employee_positions_to_delete)

        for man_acc, units in account_manager_positions.items():
            manager_positions_to_delete = Position.managers.filter(
                account=man_acc, imported=True).exclude(unit__in=units)
            if manager_positions_to_delete:
                to_delete.append(manager_positions_to_delete)

    def add_account(
        obj: dict[str, Any],
        person_type: Role
    ) -> None:
        """
        Add account for either a MO employee or a MO manager.

        Args:
            obj: the GraphQL object containing the person, i.e. an employee
                 object or a manager object.
            person_type: the type of person, i.e. an employee or a manager.
        """

        persons = obj.get("person")
        if persons is None:
            return

        try:
            person = one(persons)
        except ValueError:
            # This should never happen
            logger.warn(
                f"Found {person_type.value} object with a number of persons different from one!"
            )
            return
        acc = evaluate_unit_member(member=person)
        if acc:
            # TODO: This feels fragile.. and potentially soon needs support for SID
            # Look to refactor from MSGraph import actions and generalize logic.
            employee_email = get_email_address(person)
            if employee_email:
                evaluate_aliases(account=acc, email=employee_email)

            positions_to_add(acc=acc, unit=unit, role=person_type)

    for org_unit_raw in [ou["current"] for ou in org_unit_list]:
        # Evaluate org units and store their parent-relations.
        unit, parent_info = evaluate_org_unit(org_unit_raw)
        parent_id = parent_info.get("uuid") if parent_info else None
        ou_parent_relations[unit] = parent_id

        for engagement in org_unit_raw.get("engagements"):
            add_account(engagement, Role.EMPLOYEE)

        for manager in org_unit_raw.get("managers"):
            add_account(manager, Role.MANAGER)

    # Sort out OU-parent relations
    for ou, parent_id in ou_parent_relations.items():
        if ou.parent != ous.get(parent_id):
            ou.parent = ous.get(parent_id) if parent_id else None
            to_update.append((ou, ("parent",)))

    # Append positions to to_delete
    positions_to_delete()
    # ... then, execute
    prepare_and_publish(organization, all_uuids, to_add, to_delete, to_update)
