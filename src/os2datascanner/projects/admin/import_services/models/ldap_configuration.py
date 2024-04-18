# The contents of this file are subject to the Mozilla Public License
# Version 2.0 (the "License"); you may not use this file except in
# compliance with the License. You may obtain a copy of the License at
#    http://www.mozilla.org/MPL/
#
# Software distributed under the License is distributed on an "AS IS"basis,
# WITHOUT WARRANTY OF ANY KIND, either express or implied. See the License
# for the specific language governing rights and limitations under the
# License.
#
# OS2datascanner is developed by Magenta in collaboration with the OS2 public
# sector open source network <https://os2.eu/>.
#
import json
import requests
import structlog

from django.conf import settings
from django.db import models
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _

from .exported_mixin import Exported
from .import_service import ImportService
from .realm import Realm
from ..keycloak_services import refresh_token
from ...adminapp.aescipher import encrypt, decrypt  # Suggestion: move to core?

logger = structlog.get_logger()


class LDAPUserAttributeMapper:
    def __init__(self, name, ldap_attr, user_attr, mandatory_in_ldap=False,
                 binary_attr=False, always_read=True, read_only=True):
        self.name = name
        self.ldap_attr = ldap_attr
        self.user_attr = user_attr
        self.mandatory_in_ldap = mandatory_in_ldap
        self.binary_attr = binary_attr
        self.always_read = always_read
        self.read_only = read_only

    def to_payload_json(self, config_id):
        return {
            "name": self.name,
            "providerId": "user-attribute-ldap-mapper",
            "providerType": "org.keycloak.storage.ldap.mappers.LDAPStorageMapper",
            "parentId": config_id,
            "config": {
                "ldap.attribute": [self.ldap_attr],
                "is.mandatory.in.ldap": [self.mandatory_in_ldap],
                "is.binary.attribute": [self.binary_attr],
                "always.read.value.from.ldap": [self.always_read],
                "read.only": [self.read_only],
                "user.model.attribute": [self.user_attr]
            }
        }


class LDAPUsernameAttributeMapper(LDAPUserAttributeMapper):
    # The username attribute field creates a mapper behind the scenes in Keycloak. Annoyingly, this
    # isn't updated when the user federation configuration is. Hence, we need a way to update it.
    def __init__(self, ldap_attr, ):
        super().__init__(name="username", ldap_attr=ldap_attr, user_attr="username")


class LDAPFirstNameAttributeMapper(LDAPUserAttributeMapper):
    def __init__(self, ldap_attr: str):
        # Most defaults are good here, we just need the AD specific attribute.
        super().__init__(name="first name", ldap_attr=ldap_attr, user_attr="firstName")


class LDAPMemberOfMapper(LDAPUserAttributeMapper):
    def __init__(self):
        # We currently don't allow any customization, it's always just memberOf
        super().__init__(name="memberOf", ldap_attr="memberOf", user_attr="memberOf")


class LDAPSIDMapper(LDAPUserAttributeMapper):
    def __init__(self, ldap_attr: str):
        # Needs to be in binary
        super().__init__(name="objectSid", ldap_attr=ldap_attr,
                         user_attr="objectSid", binary_attr=True)


# NOTE: all help-texts are copied from the equivalent form in Keycloak admin
class LDAPConfig(Exported, ImportService):
    vendor = models.CharField(
        max_length=32,
        choices=[
            ('ad', _('Active Directory')),
            ('other', _('other').capitalize()),
        ],
        verbose_name=_('vendor'),
    )
    import_into = models.CharField(
        max_length=32,
        choices=[
            ('group', _('groups').capitalize()),
            ('ou', _('organizational units').capitalize()),
        ],
        default='ou',
        verbose_name=_("import users into"),
    )
    username_attribute = models.CharField(
        max_length=64,
        help_text=_(
            "Name of LDAP attribute, which is mapped as username. "
            "For many LDAP server vendors it can be 'uid'. "
            "For Active Directory it can be 'sAMAccountName' or 'cn'. "
            "The attribute should be filled for all LDAP user records you "
            "want to import from LDAP."
        ),
        verbose_name=_('username LDAP attribute'),
    )
    firstname_attribute = models.CharField(
        max_length=64,
        help_text=_(
            "Name of the LDAP attribute which is mapped as first name. "
            "For many LDAP server vendors it can be 'givenName'"
        ),
        verbose_name=_("First name LDAP attribute"),
        # We're too late to the party, not setting a default value as it is AD vendor dependant.
        # If not populated, we're sticking to whatever Keycloak does behind the scenes.
        null=True,
        blank=True
    )

    rdn_attribute = models.CharField(
        max_length=64,
        help_text=_(
            "Name of LDAP attribute, which is used as RDN of typical user DN. "
            "Usually, but not necessarily, the same as username LDAP attribute."
            " For example for Active Directory, it is common to use 'cn' as "
            "RDN attribute when username attribute might be 'sAMAccountName'."
        ),
        verbose_name=_('RDN LDAP attribute'),
    )
    uuid_attribute = models.CharField(
        max_length=64,
        help_text=_(
            "Name of LDAP attribute, which is used as unique object identifier "
            "(UUID) for objects in LDAP. For many LDAP server vendors, "
            "it is 'entryUUID'; however some are different. "
            "For example for Active Directory it should be 'objectGUID'. "
            "If your LDAP server does not support the notion of UUID, "
            "you can use any other attribute that is supposed to be unique "
            "among LDAP users in the tree. For example 'uid' or 'entryDN'."
        ),
        verbose_name=_('UUID LDAP attribute'),
    )
    object_sid_attribute = models.CharField(
        max_length=64,
        blank=True,
        null=True,
        help_text=_(
            "Name of LDAP attribute, which stores the object security identifier. (SID) "
            "Often this is stored as 'objectSid' or 'securityIdentifier'. "
            "Without this attribute, OSdatascanner will not be able to identify the owner "
            "of on-premise files."
        ),
        verbose_name=_("Object security identifier")
    )
    user_obj_classes = models.TextField(
        help_text=_(
            "All values of LDAP objectClass attribute for users in LDAP "
            "divided by comma. For example: "
            "'inetOrgPerson, organizationalPerson'. "
            "User records are only imported if they have all those classes."
        ),
        verbose_name=_('user object classes'),
    )
    custom_user_filter = models.TextField(
        blank=True,
        null=True,
        help_text=_(
            "Additional LDAP Filter for filtering searched users. "
            "Leave this empty if you don't need additional filter. "
            "Make sure that it starts with '(' and ends with ')'"
        ),
        verbose_name=_('custom LDAP user filter'),
    )

    connection_protocol = models.CharField(
        max_length=8,
        choices=(('ldap://', 'ldap'), ('ldaps://', 'ldaps')),
        default='ldaps://',
        help_text=_(
            "Choose between an encrypted connection protocol (ldaps) or an "
            "unencrypted one (ldap). Only select the unencrypted protocol if "
            "absolutely necessary."
        ),
        verbose_name=_('connection protocol'),
    )
    connection_url = models.CharField(
        max_length=256,
        help_text=_(
            "Connection URL to the LDAP server. "
        ),
        verbose_name=_('connection URL'),
    )
    users_dn = models.TextField(
        help_text=_(
            "Distinguished name for the (top) OU in which to search for "
            "users. Groups present under this OU will not necessarily be "
            "imported, as OSdatascanner reconstructs groups based on users' "
            "group memberships."
        ),
        verbose_name=_('DN for users (OU)'),
    )
    search_scope = models.PositiveSmallIntegerField(
        choices=(
            (1, _('one level').capitalize()),
            (2, _('subtree').capitalize()),
        ),
        help_text=_(
            "For one level, the search applies only for users in the DNs "
            "specified by User DNs. "
            "For subtree, the search applies to the whole subtree. "
            "See LDAP documentation for more details."
        ),
        verbose_name=_('search scope'),
    )
    bind_dn = models.TextField(
        help_text=_(
            "Distinguished name for the service account allowing access to LDAP"
        ),
        verbose_name=_('LDAP service account user name'),
    )
    # Initialization vector for decryption
    _iv_ldap_credential = models.BinaryField(
        db_column='iv_ldap',
        max_length=32,
        blank=True,
        null=False,
        verbose_name='initialization vector for ldap credential',
    )
    # Encrypted credential
    _cipher_ldap_credential = models.BinaryField(
        db_column='cipher_ldap',
        max_length=1024,
        blank=True,
        null=False,
        verbose_name='cipher text for ldap credential',
    )

    @property
    def ldap_credential(self):
        return decrypt(self._iv_ldap_credential,
                       bytes(self._cipher_ldap_credential))

    @property
    def realm(self):
        realm = get_object_or_404(Realm, organization_id=self.pk)
        return realm

    @ldap_credential.setter
    def ldap_credential(self, value):
        self._iv_ldap_credential, self._cipher_ldap_credential = encrypt(value)

    def rotate_credential(self, key=None):
        credential = self.ldap_credential
        self._iv_ldap_credential, self._cipher_ldap_credential = encrypt(credential, key)

    class Meta:
        verbose_name = _('LDAP configuration')
        verbose_name_plural = _('LDAP configurations')

    def get_payload_dict(self):
        full_connection_url = self.connection_protocol + self.connection_url
        return {
            "name": "ldap",
            "providerId": "ldap",
            "providerType": "org.keycloak.storage.UserStorageProvider",
            "parentId": self.realm.pk,
            "id": str(self.pk),
            "config": {
                "enabled": ["true"],
                "priority": ["0"],
                "fullSyncPeriod": ["-1"],
                "changedSyncPeriod": ["-1"],
                "cachePolicy": ["DEFAULT"],
                "evictionDay": [],
                "evictionHour": [],
                "evictionMinute": [],
                "maxLifespan": [],
                "batchSizeForSync": ["1000"],
                "editMode": ['READ_ONLY'],
                "importEnabled": ["true"],
                "syncRegistrations": ["false"],
                "vendor": [self.vendor],
                "usePasswordModifyExtendedOp": [],
                "usernameLDAPAttribute": [self.username_attribute],
                "rdnLDAPAttribute": [self.rdn_attribute],
                "uuidLDAPAttribute": [self.uuid_attribute],
                "userObjectClasses": [self.user_obj_classes],
                "connectionUrl": [full_connection_url],
                "usersDn": [self.users_dn],
                "authType": ["simple"],
                "startTls": [],
                "bindDn": [self.bind_dn],
                "bindCredential": [self.ldap_credential],
                "customUserSearchFilter": [self.custom_user_filter],
                "searchScope": [str(self.search_scope)],
                "validatePasswordPolicy": ["false"],
                "trustEmail": ["false"],
                "useTruststoreSpi": ["ldapsOnly"],
                "connectionPooling": ["true"],
                "connectionPoolingAuthentication": [],
                "connectionPoolingDebug": [],
                "connectionPoolingInitSize": [],
                "connectionPoolingMaxSize": [],
                "connectionPoolingPrefSize": [],
                "connectionPoolingProtocol": [],
                "connectionPoolingTimeout": [],
                "connectionTimeout": [],
                "readTimeout": [],
                "pagination": ["true"],
                "allowKerberosAuthentication": ["false"],
                "serverPrincipal": [],
                "keyTab": [],
                "kerberosRealm": [],
                "debug": ["false"],
                "useKerberosForPasswordAuthentication": ["false"]
            }
        }

    # API calls
    @refresh_token
    def get_mappers(self, token=None):
        url = (settings.KEYCLOAK_BASE_URL +
               f'/auth/admin/realms/{str(self.realm)}/components?parent={str(self.pk)}'
               f'&type=org.keycloak.storage.ldap.mappers.LDAPStorageMapper')

        headers = {
            'Authorization': f'bearer {token}',
            'Content-Type': 'application/json;charset=utf-8',
        }

        return requests.get(url, headers=headers)

    @refresh_token
    def update_or_create_user_attr_mapper(self, mapper: LDAPUserAttributeMapper, token=None):

        headers = {
            'Authorization': f'bearer {token}',
            'Content-Type': 'application/json;charset=utf-8',
        }

        # API call - gets existing mappers in json format - returns a list of dictionaries.
        existing_mappers = self.get_mappers(token=token).json()
        # Unpack - if there is an existing one, we need its id.
        name_to_id = {d["name"]: d["id"] for d in existing_mappers}
        mapper_id = name_to_id.get(mapper.name)

        payload = mapper.to_payload_json(config_id=str(self.pk))

        if mapper_id:  # Means there's an existing mapper
            url = (settings.KEYCLOAK_BASE_URL +
                   f'/auth/admin/realms/{str(self.realm)}/components/{mapper_id}')
            logger.info(f"Existing mapper: {mapper.name} found! Updating it..")
            return requests.put(url, data=json.dumps(payload), headers=headers)

        else:  # Means there isn't an existing one - create it.
            url = (settings.KEYCLOAK_BASE_URL + f'/auth/admin/realms/{str(self.realm)}/components/')
            logger.info(f"No mapper: {mapper.name} found! Creating one..")
            return requests.post(url, data=json.dumps(payload), headers=headers)
