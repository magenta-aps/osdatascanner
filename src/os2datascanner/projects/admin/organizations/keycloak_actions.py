import base64
import struct
import structlog
from enum import Enum
from typing import Tuple, Sequence, Iterator, Any
from itertools import chain
from os2datascanner.utils.ldap import RDN, LDAPNode
from .utils import prepare_and_publish
from os2datascanner.utils.section import suppress_django_signals
from ..import_services.models.realm import Realm
from ..import_services import keycloak_services
from .models import (Alias, Account, Position,
                     Organization, OrganizationalUnit)
from .models.aliases import AliasType

logger = structlog.get_logger("admin_organizations")
# TODO: Place somewhere reusable, or find a smarter way to ID aliases imported_id..
EMAIL_ALIAS_IMPORTED_ID_SUFFIX = "/email"
SID_ALIAS_IMPORTED_ID_SUFFIX = "/sid"


class Action(Enum):
    NOTHING = 0
    DELETE = 1
    ADD = 2
    UPDATE = 3
    KEEP = 4


def keycloak_dn_selector(d):
    attributes = d.get("attributes", {})
    name = attributes.get("LDAP_ENTRY_DN", [None])[0]
    if name:
        yield name


def keycloak_group_dn_selector(d):
    attributes = d.get("attributes", {})
    name = attributes.get("LDAP_ENTRY_DN", [None])[0]
    if name:
        dn = RDN.dn_to_sequence(name)
        if group_dn := attributes.get("group_dn", None):
            gdn = RDN.dn_to_sequence(group_dn)
            yield RDN.sequence_to_dn(gdn + (dn[-1],))

        elif groups := attributes.get("memberOf", []):
            # XXX: Deprecated - we don't import memberOf anymore
            for group_name in groups:
                gdn = RDN.dn_to_sequence(group_name)
                if gdn:  # Only yield names for valid groups
                    yield RDN.sequence_to_dn(gdn + (dn[-1],))


def _dummy_pc(action, *args):
    pass


def perform_import(  # noqa: CCR001, too high cognitive complexity
        realm: Realm,
        progress_callback=_dummy_pc) -> Tuple[int, int, int]:
    """Collects the user hierarchy from the specified realm and creates
    local OrganizationalUnits and Accounts to reflect it. Local objects
    previously imported by this function but no longer backed by an object
    returned by Keycloak will be deleted.

    Returns a tuple of counts of objects that were added, updated, and
    removed."""
    org = realm.organization
    import_service = org.importservice
    account_dn_managed_units_paths = {}
    if not import_service or not import_service.ldapconfig:
        return 0, 0, 0

    name_selector = keycloak_dn_selector
    if import_service.ldapconfig.import_into == "group":
        name_selector = keycloak_group_dn_selector

    token = keycloak_services.request_access_token()
    # Timeout set to 30 minutes
    sync_message = keycloak_services.sync_users(
            realm.realm_id, realm.organization.pk, token=token, timeout=1800)
    sync_message.raise_for_status()

    # If the client doesn't have a group_filter_mapper they haven't updated their ldap config
    mappers = import_service.ldapconfig.get_mappers(token=token).json()
    has_group_filter = any(mapper['name'] == "group_filter_mapper" for mapper in mappers)
    if import_service.ldapconfig.import_into == "group" and not has_group_filter:
        logger.debug("LDAP configuration not updated. Importing without group filter.")

    # TODO: In the future this kind of logic should be reimplemented using
    # websockets.
    # Timeout set to 30 minutes
    if import_service.ldapconfig.import_into == "group" and has_group_filter:
        # Gets all groups in the realm, and then gets every member of the groups

        # List object of all groups in realm
        group_list = list(keycloak_services.iter_groups(realm.realm_id, token=token, timeout=1800))

        # If the import_managers attribute is enabled, get the group managers
        if import_service.ldapconfig.import_managers:
            for group in group_list:
                if group["attributes"].get("managedBy"):
                    if account_dn_managed_units_paths.get(
                            group["attributes"]["managedBy"][0]) is None:
                        account_dn_managed_units_paths[group["attributes"]["managedBy"][0]] = []
                    account_dn_managed_units_paths[group["attributes"]["managedBy"][0]].append(
                        RDN.dn_to_sequence(group["attributes"]["distinguishedName"][0]))

        def user_iter(groups):
            for group in groups:
                members = keycloak_services.iter_group_members(
                    realm.realm_id, group['id'], group["attributes"]["distinguishedName"][0],
                    token=token, timeout=1800, page_size=1000
                )
                yield from members

        # Gets all users in a group in given realm
        all_users = user_iter(iter(group_list))
    else:
        # Gets all users in the given realm
        all_users = keycloak_services.iter_users(
                        realm.realm_id, token=token, timeout=1800, page_size=1000)

    return perform_import_raw(
        org,
        all_users,
        name_selector,
        progress_callback=progress_callback,
        account_dn_managed_units_paths=account_dn_managed_units_paths,
        do_manager_import=import_service.ldapconfig.import_managers)


def _account_to_node(a: Account) -> LDAPNode:
    """Constructs a LDAPNode from an Account object."""
    local_path_part = RDN.dn_to_sequence(a.imported_id)[-1:]
    return LDAPNode.make(
            local_path_part,
            attributes={"LDAP_ENTRY_DN": [a.imported_id]},
            id=str(a.uuid),
            firstName=a.first_name,
            lastName=a.last_name)


def _unit_to_node(
        ou: OrganizationalUnit, *,
        parent_path: Sequence[RDN] = ()) -> LDAPNode:
    """Constructs a LDAPNode hierarchy from an OrganizationalUnit object,
    including nodes for every sub-unit and account."""
    full_path = (
            RDN.dn_to_sequence(ou.imported_id) if ou.imported_id else ())
    local_path_part = RDN.drop_start(full_path, parent_path)
    return LDAPNode.make(
            local_path_part,
            *(_unit_to_node(c, parent_path=full_path)
              for c in ou.children.filter(imported=True)),
            *(_account_to_node(c) for c in ou.account_set.filter(imported=True)))


def _node_to_iid(path: Sequence[RDN], node: LDAPNode) -> str:
    """Generates the Imported.imported_id for an LDAPNode at a specified
    position in the hierarchy.

    For organisational units, this will just be the DN specified by the
    hierarchy, as OUs have no independent existence in OS2datascanner. For
    users, though, the canonical DN is used instead, as a user might appear at
    multiple positions (if they're a member of several groups, for example.)"""
    if node.children:  # The node is a group/OU
        return RDN.sequence_to_dn(path)
    else:  # The node is a user
        return node.properties["attributes"]["LDAP_ENTRY_DN"][0]


def _convert_sid(sid):
    # We'll need it in bytes first.
    b_sid = base64.decodebytes(sid.encode())

    if b_sid.startswith(b"S-1-"):
        return b_sid.decode()  # Plaintext SID (from Samba?) Useful for openLDAP testing

    def __convert_binary_sid_to_str(binary_sid):
        # This code is sourced from:
        # noqa: https://stackoverflow.com/questions/33188413/python-code-to-convert-from-objectsid-to-sid-representation
        # We could also install samba and use its functionality.
        version = struct.unpack('B', binary_sid[0:1])[0]
        # I do not know how to treat version != 1 (it does not exist yet)
        try:
            if not version == 1:
                raise ValueError(f"Invalid version! {version}")
            length = struct.unpack('B', binary_sid[1:2])[0]
            authority = struct.unpack(b'>Q', b'\x00\x00' + binary_sid[2:8])[0]
            string = 'S-%d-%d' % (version, authority)
            binary = binary_sid[8:]
            if not len(binary) == 4 * length:
                raise ValueError(f"Invalid length of binary! {len(binary)}")
            for i in range(length):
                value = struct.unpack('<L', binary[4*i:4*(i+1)])[0]
                string += '-%d' % value
            return string
        except ValueError as ve:
            logger.exception(f"{ve} "
                             f"Unable to process SID format! Will skip.")
            return None

    return __convert_binary_sid_to_str(b_sid)


def _path_to_unit(org: Organization,
                  path: Sequence[RDN],
                  units: dict[Sequence[RDN], OrganizationalUnit]
                  ) -> tuple[OrganizationalUnit | None, bool]:
    """Gets or creates a unit from a path, and returns whether or not the unit is new."""
    unit_id = RDN.sequence_to_dn(path)
    unit = units.get(path)
    initialized = False
    if unit is None:
        try:
            unit = OrganizationalUnit.objects.get(organization=org, imported_id=unit_id)
        except OrganizationalUnit.DoesNotExist:
            label = path[-1].value if path else ""

            # We can't just call path_to_unit(o, path[:-1]) here, because
            # we have to make sure that our units actually match what the
            # hierarchy specifies without creating extra nodes
            parent = None
            if path:
                path_fragment = path[:-1]
                while path_fragment and not parent:
                    parent = units.get(path_fragment)
                    path_fragment = path_fragment[:-1]

            unit = OrganizationalUnit(
                    imported_id=unit_id,
                    name=label, parent=parent, organization=org,
                    # Clear the MPTT tree fields for now -- they get
                    # recomputed after we do bulk_create
                    lft=0, rght=0, tree_id=0, level=0)
            initialized = True
    return unit, initialized


def _node_to_account(org: Organization, node: LDAPNode, accounts: list[Account]
                     ) -> tuple[Account, bool]:
    """Gets or creates an account from a node, and returns whether or not it us new."""
    # One Account object can have multiple paths (if it's a member of
    # several groups, for example), so we need to use the true DN as our
    # imported_id here
    account_id = node.properties["attributes"]["LDAP_ENTRY_DN"][0]
    account = None
    for acc in accounts:
        # If the account already exists in accounts, use it
        if acc.imported_id == account_id:
            account = acc
            break
    initialized = False
    if account is None:
        try:
            account = Account.objects.get(
                    organization=org, imported_id=account_id)
        except Account.DoesNotExist:
            account = Account(organization=org, imported_id=account_id,
                              uuid=node.properties["id"])
            initialized = True
    return account, initialized


def _get_iids_of_hiearchy(hierarchy: LDAPNode) -> set[str]:
    """Gets all iids of a LDAP-hiearchy."""
    iids = set()
    for path, r in hierarchy.walk():
        if not path:
            continue
        iids.add(_node_to_iid(path, r))
    return iids


def _create_unit_hierarchy(remote_hierarchy: LDAPNode,
                           org: Organization
                           ) -> tuple[dict[Sequence[RDN], OrganizationalUnit],
                                      list[OrganizationalUnit]]:
    """For every Organizational Unit in the remote hierarchy, create a corresponding one locally.
     Returns a dict from path to unit and a list of units that were added"""
    path_to_unit = {}
    new_units = []
    for path, node in remote_hierarchy.walk():
        if not path:
            continue

        if not node.children:
            # If a node doesn't have children, it's either a user or an uninteresting OU
            continue
        unit, new = _path_to_unit(org, path, path_to_unit)
        path_to_unit[path] = unit
        if new:
            new_units.append(unit)

    return path_to_unit, new_units


def _handle_diff(path: Sequence[RDN],
                 local: LDAPNode,
                 remote: LDAPNode,
                 org: Organization,
                 accounts: list[Account],
                 progress_callback=_dummy_pc
                 ) -> tuple[Action, OrganizationalUnit | Account | None]:
    """Given a local and remote node with the same path
     finds the necessary action in case of any difference."""
    if not path:
        # Ignore the contentless root node
        progress_callback("diff_ignored", path)
        return (Action.NOTHING, None)

    # Keycloak's UserRepresentation type has no required fields(!); we
    # can't do anything useful if we don't have the very basics, though
    if remote and not all(n in remote.properties for n in ("id", "attributes", "username",)):
        progress_callback("diff_ignored", path)
        return (Action.NOTHING, None)

    iid = _node_to_iid(path, remote or local)

    if local and not remote:
        # A local object with no remote counterpart
        logger.debug(f"local node: {local}, remote node: {remote}, deleting")
        try:
            obj = (Account.objects.get(imported_id=iid))
        except Account.DoesNotExist:
            obj = (OrganizationalUnit.objects.get(imported_id=iid))
        return (Action.DELETE, obj)

    if remote and not local:
        # A remote user exists and it doesn't have a local counterpart. Create one
        try:
            acc, new = _node_to_account(org, remote, accounts)
            return (Action.ADD, acc) if new else (Action.KEEP, acc)
        except KeyError:
            # Missing required attribute -- skip this object
            progress_callback("diff_ignored", path)
            return (Action.NOTHING, None)

    # A remote user exists and it has a local counterpart. Don't do anything (yet)
    return (Action.NOTHING, None)


def _get_accounts(hierarchy: LDAPNode) -> list[tuple[Account, Sequence[RDN], LDAPNode]]:
    """Returns all accounts in both remote and local hierarchy,
      along with their corresponding path and remote node"""
    accounts = []

    for path, local, remote in hierarchy:
        if not path or not local or not remote or remote.children:
            # This is either not an account or it doesn't exist in remote or local. Skip it
            continue

        # Keycloak's UserRepresentation type has no required fields(!); we
        # can't do anything useful if we don't have the very basics, though
        if remote and not all(n in remote.properties for n in ("id", "attributes", "username",)):
            continue

        iid = _node_to_iid(path, remote or local)
        try:
            account = Account.objects.get(imported_id=iid)
        except Account.DoesNotExist:
            # This can only happen if an Account has changed its
            # imported ID without changing its position in the tree
            # (i.e., a user's DN has changed, but their group
            # membership has not). Retrieve the object by the old ID --
            # we'll update it in a moment
            account = Account.objects.get(
                    imported_id=_node_to_iid(path, local))

        accounts.append((account, path, remote))
    return accounts


def _update_alias(account: Account, value, alias_type: AliasType, id: str
                  ) -> Iterator[tuple[Action, Any]]:
    """Helper function for _update_account.
     Updates the aliases of the given type of the given account."""
    if value:
        try:
            alias = Alias.objects.get(
                imported_id=id,
                account=account,
                _alias_type=alias_type)
            yield (Action.KEEP, alias)
            for attr_name, expected in (("_value", value),):
                if getattr(alias, attr_name) != expected:
                    setattr(alias, attr_name, expected)
                    yield (Action.UPDATE, (alias, (attr_name,)))
        except Alias.DoesNotExist:
            alias = Alias(
                imported_id=id,
                account=account,
                _alias_type=alias_type,
                _value=value
            )
            yield (Action.ADD, alias)
    elif not value:
        for alias in Alias.objects.filter(account=account,
                                          imported=True,
                                          _alias_type=alias_type):
            yield (Action.DELETE, alias)


def _update_account(account: Account, path: Sequence[RDN], remote_node: LDAPNode
                    ) -> Iterator[tuple[Action, Any]]:
    """Updates an Accounts properties and aliases to match its remote node."""
    mail_address = remote_node.properties.get("email")

    # SID is hidden a level further down, we'll have to unpack...
    object_sid = None
    sid_attr = remote_node.properties.get("attributes", {}).get("objectSid")
    if sid_attr:
        object_sid = _convert_sid(sid_attr[0])

    imported_id = f"{account.imported_id}{EMAIL_ALIAS_IMPORTED_ID_SUFFIX}"
    imported_id_sid = f"{account.imported_id}{SID_ALIAS_IMPORTED_ID_SUFFIX}"

    for action in _update_alias(account, mail_address, AliasType.EMAIL, imported_id):
        yield action
    for action in _update_alias(account, object_sid, AliasType.SID, imported_id_sid):
        yield action

    iid = _node_to_iid(path, remote_node)
    # Update the other properties of the account
    for attr_name, expected in (
            ("imported_id", iid),
            ("username", remote_node.properties["username"]),
            # Our database schema requires the name properties, so use the
            # empty string as the dummy value instead of None
            ("first_name", remote_node.properties.get("firstName", "")),
            ("last_name", remote_node.properties.get("lastName", "")),
            ("email", remote_node.properties.get("email", ""))):
        if getattr(account, attr_name) != expected:
            setattr(account, attr_name, expected)
            yield (Action.UPDATE, (account, (attr_name,)))


def _update_account_position(account: Account,
                             account_positions: dict[Account, list[OrganizationalUnit]],
                             unit: OrganizationalUnit
                             ) -> Iterator[tuple[Action, Position | None]]:
    """Given an Account and an Organizational Unit, adds the unit to the accounts
     list of units in account_positions.
     Adds a Position object of account in unit, if one doesn't exist already."""
    if account not in account_positions:
        account_positions[account] = []
    account_positions[account].append(unit)

    if Position.employees.filter(
                account__imported_id=account.imported_id,
                unit=unit, imported=True).exists():
        # account is already an employee of unit. No need to do anything
        return (Action.NOTHING, None)
    else:
        position = Position(
            imported=True,
            account=account,
            unit=unit)
        # Position is missing. Add it
        return (Action.ADD, position)


def _filter_positions(account_positions: dict[Account, list[OrganizationalUnit]]
                      ) -> Iterator[tuple[Action, Position]]:
    """Finds every position for each given account that isn't accurate."""
    for acc in account_positions:
        for pos in Position.employees.filter(
                    account=acc, imported=True).exclude(
                    unit__in=account_positions[acc]):
            yield (Action.DELETE, pos)


def _update_manager_positions(accounts: set[Account],
                              account_dn_managed_units_paths: dict[str, list[Sequence[RDN]]],
                              org: Organization,
                              path_to_unit: dict[Sequence[RDN], OrganizationalUnit]
                              ) -> Iterator[tuple[Action, Position]]:
    """Creates a Position object for every group with managedBy and user in a group
    in remote_hierarchy."""

    for account in accounts:
        units = [unit.imported_id for unit in account.get_managed_units()]
        for group_dn in account_dn_managed_units_paths.get(account.imported_id, []):
            if group_dn not in units and not Position.managers.filter(
                account=account, unit=_path_to_unit(
                    org, group_dn, path_to_unit)[0], imported=True).exists():
                position = Position(
                            imported=True,
                            account=account,
                            unit=_path_to_unit(org, group_dn, path_to_unit)[0],
                            role="manager")
                # Position is missing. Add it
                yield (Action.ADD, position)


def _filter_manager_positions(
        accounts: set[Account], account_dn_managed_units_paths: dict[str, list[Sequence[RDN]]]
        ) -> Iterator[Position]:
    """Finds every manager position for each given account that isn't accurate."""
    for account in accounts:
        units_imported_ids = [unit.imported_id for unit in account.get_managed_units()]
        account_dn_managed_units_paths_units = [
            RDN.sequence_to_dn(unit) for unit in account_dn_managed_units_paths.get(
                account.imported_id, [])]
        for unit in units_imported_ids:
            if unit not in account_dn_managed_units_paths_units:
                yield from Position.managers.filter(
                        account=account, unit__imported_id=unit, imported=True)


@suppress_django_signals
def perform_import_raw(  # noqa: CCR001, too high cognitive complexity
        org: Organization,
        remote,
        name_selector,
        progress_callback=_dummy_pc,
        account_dn_managed_units_paths=None,
        do_manager_import=False):
    """The main body of the perform_import function, spun out into a separate
    function to allow for easier testing. Constructs a LDAPNode hierarchy from
    a Keycloak JSON response, compares it to an organisation's local hierarchy,
    and adds, updates and removes database objects to bring the local hierarchy
    into sync.

    Returns a tuple of counts of objects that were added, updated, and
    removed."""

    # XXX: is this correct? It seems to presuppose the existence of a top unit,
    # which the database doesn't actually specify or require
    local_top = OrganizationalUnit.objects.filter(
        imported=True, parent=None, organization=org).first()

    # Convert the local objects to a LDAPNode so that we can use its diff
    # operation
    local_hierarchy = (
            _unit_to_node(local_top)
            if local_top
            else LDAPNode.make(()))

    remote_hierarchy = LDAPNode.from_iterator(
            remote, name_selector=name_selector)

    # Dict keeping track of what actions should be applied to the database
    actions = {a: [] for a in Action}

    iids_to_preserve = _get_iids_of_hiearchy(remote_hierarchy)

    if not iids_to_preserve:
        logger.warning(
                "no remote users or organisational units available for"
                f" organisation {org.name}; are you sure your LDAP settings"
                " are correct?")
        return 0, 0, 0

    # Make sure that we have an OrganizationalUnit hierarchy that reflects the remote one
    path_to_unit, new_units = _create_unit_hierarchy(remote_hierarchy, org)
    actions[Action.ADD].extend(new_units)

    logger.info("Constructing raw diff")

    diff = list(local_hierarchy.diff(remote_hierarchy))
    progress_callback("diff_computed", len(diff))

    # Holds every account found, along with their path and remote node
    account_path_node = []
    for acc, path, remote in _get_accounts(diff):
        account_path_node.append((acc, path, remote))
        actions[Action.KEEP].append(acc)

    accounts = [acc for (acc, _, _) in account_path_node]
    for path, local_node, remote_node in diff:
        a, obj = _handle_diff(path, local_node, remote_node, org, accounts, progress_callback)
        actions[a].append(obj)
        if a in (Action.ADD, Action.KEEP) and isinstance(obj, Account):
            # This account wasn't found during _get_accounts. Add it to accounts
            account_path_node.append((obj, path, remote_node))
            accounts.append(obj)

    # dict(account : units they are part of). Is populated in _update_account_position.
    account_positions = {}
    # Each Account should only be updated once. Keep track of those already updated
    updated_accounts = set()
    for acc, path, remote_node in account_path_node:
        a, obj = _update_account_position(acc, account_positions, path_to_unit[path[:-1]])
        actions[a].append(obj)

        # Accounts should only be updated once
        if acc in updated_accounts:
            continue
        for a, obj in _update_account(acc, path, remote_node):
            actions[a].append(obj)
        updated_accounts.add(acc)

    # Figure out which positions to delete for each user.
    for action, object in _filter_positions(account_positions):
        actions[action].append(object)

    # If we have managedBy accounts, we need to update the manager positions
    if do_manager_import:
        for action, position in _update_manager_positions(
                updated_accounts,
                account_dn_managed_units_paths,
                org=org,
                path_to_unit=path_to_unit):
            actions[action].append(position)

        for position in _filter_manager_positions(
                updated_accounts, account_dn_managed_units_paths):
            actions[Action.DELETE].append(position)

    # Make sure we don't try to delete objects that are still referenced in the remote hierarchy
    for obj in chain(actions[Action.KEEP], actions[Action.ADD]):
        iids_to_preserve.add(obj.imported_id)
    actions[Action.DELETE] = [t for t in actions[Action.DELETE]
                              if t.imported_id not in iids_to_preserve]

    prepare_and_publish(org, iids_to_preserve,
                        actions[Action.ADD], [actions[Action.DELETE]], actions[Action.UPDATE])

    return len(actions[Action.ADD]), len(actions[Action.UPDATE]), len(actions[Action.DELETE])
