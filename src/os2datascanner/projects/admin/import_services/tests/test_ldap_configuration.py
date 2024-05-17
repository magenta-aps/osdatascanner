import json

import pytest
from django.utils.timezone import now

from ..models import Realm, LDAPConfig


@pytest.fixture
def ldap_conf(test_org):
    Realm.objects.create(
        realm_id=test_org.slug,
        organization=test_org,
        last_modified=now(),
    )
    config = LDAPConfig.objects.create(
        organization=test_org,
        vendor="other",
        username_attribute="cn",
        rdn_attribute="cn",
        uuid_attribute="uidNumber",
        user_obj_classes="inetOrgPerson, organizationalPerson",
        connection_protocol="ldap://",
        connection_url="ldap_server:389",
        users_dn="ou=TestUnit,dc=magenta,dc=test",
        search_scope=2,
        bind_dn="cn=admin,dc=magenta,dc=test",
        last_modified=now(),
    )
    return config


@pytest.mark.django_db
class TestLDAPConfigTest:

    def test_payload(self, ldap_conf):
        ldap_conf.ldap_credential = "testMAG"
        expected_json = '{"name": "ldap", "providerId": "ldap", "providerType": "org.keycloak.storage.UserStorageProvider", "parentId": "test_org", "id": "3d6d288f-b75f-43e2-be33-a43803cd1243", "config": {"enabled": ["true"], "priority": ["0"], "fullSyncPeriod": ["-1"], "changedSyncPeriod": ["-1"], "cachePolicy": ["DEFAULT"], "evictionDay": [], "evictionHour": [], "evictionMinute": [], "maxLifespan": [], "batchSizeForSync": ["1000"], "editMode": ["READ_ONLY"], "importEnabled": ["true"], "syncRegistrations": ["false"], "vendor": ["other"], "usePasswordModifyExtendedOp": [], "usernameLDAPAttribute": ["cn"], "rdnLDAPAttribute": ["cn"], "uuidLDAPAttribute": ["uidNumber"], "userObjectClasses": ["inetOrgPerson, organizationalPerson"], "connectionUrl": ["ldap://ldap_server:389"], "usersDn": ["ou=TestUnit,dc=magenta,dc=test"], "authType": ["simple"], "startTls": [], "bindDn": ["cn=admin,dc=magenta,dc=test"], "bindCredential": ["testMAG"], "customUserSearchFilter": [null], "searchScope": ["2"], "validatePasswordPolicy": ["false"], "trustEmail": ["false"], "useTruststoreSpi": ["ldapsOnly"], "connectionPooling": ["true"], "connectionPoolingAuthentication": [], "connectionPoolingDebug": [], "connectionPoolingInitSize": [], "connectionPoolingMaxSize": [], "connectionPoolingPrefSize": [], "connectionPoolingProtocol": [], "connectionPoolingTimeout": [], "connectionTimeout": [], "readTimeout": [], "pagination": ["true"], "allowKerberosAuthentication": ["false"], "serverPrincipal": [], "keyTab": [], "kerberosRealm": [], "debug": ["false"], "useKerberosForPasswordAuthentication": ["false"]}}'  # noqa
        assert json.dumps(ldap_conf.get_payload_dict()) == expected_json
