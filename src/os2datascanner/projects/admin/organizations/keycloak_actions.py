import base64
import struct
import structlog
from typing import Tuple, Sequence, Optional
from os2datascanner.utils.ldap import RDN, LDAPNode
from .utils import prepare_and_publish
from ..import_services import keycloak_services
from .models import Alias, Account, Position, OrganizationalUnit
from .models.aliases import AliasType
from os2datascanner.projects.admin.import_services.models.errors import LDAPNothingImportedWarning
from django.utils.translation import gettext_lazy as _
from os2datascanner.core_organizational_structure.models.position import Role
from django.db.models import Q

logger = structlog.get_logger("admin_organizations")
# TODO: Place somewhere reusable, or find a smarter way to ID aliases imported_id..
ALIAS_TYPE_IMPORTED_ID_SUFFIX = {
    AliasType.EMAIL: "/email",
    AliasType.SID: "/sid",
    AliasType.USER_PRINCIPAL_NAME: "/upn",
}


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


class KeycloakImporter:
    """I keycloak importer takes a realm and uses it to import an organization through keycloak.
    A KeycloakImporter object is only intended to be used once, but can be reset using reset()."""

    def __init__(self, realm, progress_callback=_dummy_pc):
        self.realm = realm
        self.org = realm.organization if realm else None
        self.progress_callback = progress_callback

        self.reset()

    def reset(self):
        self.to_add = []
        self.to_update = []
        self.to_delete = []

        self.iids = set()
        self.accounts = {}
        self.org_units = {}
        self.account_employee_positions = {}
        self.account_manager_positions = {}

    def perform_import(self) -> Tuple[int, int, int]:  # noqa: CCR001, too high cognitive complexity
        import_service = self.org.importservice

        if not import_service or not import_service.ldapconfig:
            return 0, 0, 0

        dn_selector = keycloak_dn_selector
        if import_service.ldapconfig.import_into == "group":
            dn_selector = keycloak_group_dn_selector

        sync_message = keycloak_services.sync_users(self.realm, self.org.pk, timeout=1800)
        sync_message.raise_for_status()

        mappers = import_service.ldapconfig.get_mappers().json()
        has_group_filter = any(mapper['name'] == "group_filter_mapper" for mapper in mappers)
        if import_service.ldapconfig.import_into == "group" and not has_group_filter:
            logger.debug("LDAP configuration not updated. Importing without group filter.")

        if import_service.ldapconfig.import_into == "group" and has_group_filter:
            def member_iter(groups):
                for group in groups:
                    if import_service.ldapconfig.import_managers and (
                            manager := group["attributes"].get("managedBy", [None])[0]):
                        dn = group["attributes"]["distinguishedName"][0]
                        if self.account_manager_positions.get(manager) is None:
                            self.account_manager_positions[manager] = {dn}
                        else:
                            self.account_manager_positions[manager].add(dn)

                    members = keycloak_services.iter_group_members(
                        self.realm, group['id'], group["attributes"]["distinguishedName"][0],
                        timeout=1800, page_size=1000
                    )
                    yield from members

            group_iter = keycloak_services.iter_groups(self.realm, timeout=1800)
            user_iter = member_iter(group_iter)
        else:
            user_iter = keycloak_services.iter_users(self.realm, timeout=1800, page_size=1000)

        return self.perform_import_raw(
            user_iter,
            dn_selector,
            do_manager_import=import_service.ldapconfig.import_managers,
        )

    def perform_import_raw(self, user_iter, dn_selector, do_manager_import=False):  # noqa: CCR001
        root_node = LDAPNode.from_iterator(user_iter, name_selector=dn_selector)

        self.traverse_node(root_node, None, [])

        if not self.iids:
            no_users_warning = _(
                            "No remote users or organisational units available for"
                            " organisation {org}; are you sure your LDAP settings"
                            " are correct?")
            logger.warning(no_users_warning.format(org=self.org.name))

            raise LDAPNothingImportedWarning(no_users_warning.format(org=self.org.name))

        for acc in self.accounts.values():
            ous = self.account_employee_positions.get(acc, [])
            for ou in ous:
                if not Position.employees.filter(account=acc, imported=True, unit=ou).exists():
                    position = Position(
                        account=acc,
                        unit=ou,
                    )
                    self.to_add.append(position)

            positions_to_delete = Position.employees.filter(
                account=acc, imported=True
            ).exclude(
                unit__in=ous,
            )
            if positions_to_delete:
                self.to_delete.append(positions_to_delete)

        if do_manager_import:
            for acc in self.accounts.values():
                ou_dns = self.account_manager_positions.get(acc.distinguished_name, [])
                # TODO: Find better way to escape dn
                ous = {self.org_units[RDN.sequence_to_dn(RDN.dn_to_sequence(dn))] for dn in ou_dns}
                for ou in ous:
                    if not Position.managers.filter(account=acc, imported=True, unit=ou).exists():
                        position = Position(
                            account=acc,
                            unit=ou,
                            role=Role.MANAGER,
                        )
                        self.to_add.append(position)

                positions_to_delete = Position.managers.filter(
                    account=acc, imported=True
                ).exclude(
                    unit__in=ous,
                )
                if positions_to_delete:
                    self.to_delete.append(positions_to_delete)

        prepare_and_publish(self.org, self.iids, self.to_add, self.to_delete, self.to_update)

        return len(self.to_add), len(self.to_update), len(self.to_delete)

    def evaluate_org_unit_node(
            self,
            node: LDAPNode,
            parent: Optional[OrganizationalUnit],
            path: Sequence[RDN]):
        """ Evaluates given ldap node representing an org unit, decides if corresponding
        local object (if any) is to be updated, a new one is to be created or no actions.
        Returns an OrganizationalUnit object."""
        dn = RDN.sequence_to_dn(path)
        name = path[-1].value if path else ""
        self.iids.add(dn)

        try:
            org_unit = OrganizationalUnit.objects.get(
                organization=self.org,
                imported=True,
                imported_id=dn,
            )

            if org_unit.name != name:
                org_unit.name = name
                self.to_update.append((org_unit, ('name',)))

            if org_unit.parent != parent:
                org_unit.parent = parent
                self.to_update.append((org_unit, ('parent',)))

        except OrganizationalUnit.DoesNotExist:
            org_unit = OrganizationalUnit(
                imported_id=dn,
                organization=self.org,
                hidden=self.org.importservice.hide_units_on_import,
                name=name,
                parent=parent,
                lft=0, rght=0, tree_id=0, level=0
            )
            self.to_add.append(org_unit)

        self.org_units[dn] = org_unit
        return org_unit

    def evaluate_account_node(self, node: LDAPNode, parent: OrganizationalUnit):
        """ Evaluates given ldap node representing an account.
        Decides if corresponding local object (if any) is to be updated,
        a new one is to be created or no actions."""
        if not all(prop in node.properties for prop in ("attributes", "username", "id")):
            # Keycloak's UserRepresentation type has no required fields(!); we
            # can't do anything useful if we don't have the very basics, though
            return

        imported_id = node.properties["attributes"]["LDAP_ID"][0]
        if account := self.accounts.get(imported_id):
            self.account_employee_positions[account].add(parent)
            return

        username = node.properties["username"]
        first_name = node.properties.get("firstName", "")
        last_name = node.properties.get("lastName", "")
        email = node.properties.get("email", "")
        dn = node.properties["attributes"]["LDAP_ENTRY_DN"][0]

        base_filter = Q(organization=self.org, imported=True)
        query_methods = (
            # Standard identifying method:
            # Find the Account with the expected imported_id.
            Q(imported_id=imported_id),

            # Deprecated method:
            # Find an Account with matching dn, and no imported_id
            # (see organization migration 0068).
            Q(imported_id__isnull=True, distinguished_name=dn),

            # Backup method:
            # The above method fails for users that have been moved in AD between
            # last pre-migration import and first post-migration import.
            # But if the user has persisted in keycloak we might be able to use their keycloak id
            # to identify the coresponding account object.
            Q(uuid=node.properties["id"]),
        )
        for q in query_methods:
            qs = Account.objects.filter(base_filter & q)
            if qs.exists():
                account = qs.first()
                break
        else:
            account = Account(
                organization=self.org,
                uuid=node.properties["id"],
            )
            self.to_add.append(account)

        for attr_name, expected in (
                ("imported_id", imported_id),
                ("distinguished_name", dn),
                ("username", username),
                ("first_name", first_name),
                ("last_name", last_name),
                ("email", email)):
            if getattr(account, attr_name) != expected:
                setattr(account, attr_name, expected)
                self.to_update.append((account, (attr_name,)))

        if email:
            self.evaluate_alias(account, email, AliasType.EMAIL)

        # Unpack the list in a dict in a dict that contains the SID...
        match node.properties:
            case {"attributes": {"objectSid": [s_v]}}:
                object_sid = _convert_sid(s_v)
                self.evaluate_alias(account, object_sid, AliasType.SID)

        # ... and the other one that contains the UPN (shame we need a separate
        # match block for that, but you only get to match one case...)
        match node.properties:
            case {"attributes": {"userPrincipalName": [upn]}}:
                self.evaluate_alias(account, upn, AliasType.USER_PRINCIPAL_NAME)

        self.iids.add(imported_id)
        self.accounts[imported_id] = account
        self.account_employee_positions[account] = {parent}

    def evaluate_alias(self, account: Account, value, alias_type: AliasType):
        suffix = ALIAS_TYPE_IMPORTED_ID_SUFFIX[alias_type]
        iid = account.imported_id + suffix
        self.iids.add(iid)
        try:
            alias = Alias.objects.get(
                imported=True,
                account=account,
                _alias_type=alias_type,
            )
        except Alias.DoesNotExist:
            alias = Alias(
                account=account,
                _alias_type=alias_type,
            )
            self.to_add.append(alias)

        if alias._value != value:
            alias._value = value
            self.to_update.append((alias, ('_value',)))
        if alias.imported_id != iid:
            alias.imported_id = iid
            self.to_update.append((alias, ('imported_id',)))

    def traverse_node(
            self,
            node: LDAPNode,
            parent: Optional[OrganizationalUnit],
            path: Sequence[RDN]):
        if node.children:
            if node.label:
                path += node.label
            org_unit = self.evaluate_org_unit_node(node, parent, path)
            for child in node.children:
                self.traverse_node(child, org_unit, path)
            if node.label:
                path.pop()
        else:
            self.evaluate_account_node(node, parent)
