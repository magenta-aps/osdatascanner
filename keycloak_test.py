import json
import requests

REALM = 'os2datascanner'
CLIENT_SECRET = 'd3407798-8ce0-4636-b975-b6102ce520df'
CUSTOM_ID_CLIENT = '83e5d884-0cb0-4b20-9d4e-a0708a366459'

SERVER = 'localkeycloak.com:8090'

token_url = f'http://{SERVER}/auth/realms/{REALM}/protocol/openid-connect/token'

payload = {
    'client_id': 'admin-cli',
    'client_secret': CLIENT_SECRET,
    'grant_type': 'client_credentials'
}

r = requests.post(token_url, data=payload)
print(r.status_code, r.url)
token = r.json()['access_token']

headers = {
    'Authorization': f'bearer {token}'
}

headers2 = {
    'Authorization': f'bearer {token}',
    'Content-Type': 'application/json;charset=utf-8'
}

ldap_payload = {
    "name": "ldap",
    "providerId": "ldap",
    "providerType": "org.keycloak.storage.UserStorageProvider",
    "parentId":"os2datascanner",
    "config": {
        "enabled":["true"],
        "priority":["0"],
        "fullSyncPeriod":["-1"],
        "changedSyncPeriod":["-1"],
        "cachePolicy":["DEFAULT"],
        "evictionDay":[],
        "evictionHour":[],
        "evictionMinute":[],
        "maxLifespan":[],
        "batchSizeForSync":["1000"],
        "editMode":["READ_ONLY"],
        "importEnabled":["true"],
        "syncRegistrations":["false"],
        "vendor":["other"],
        "usePasswordModifyExtendedOp":[],
        "usernameLDAPAttribute":["cn"],
        "rdnLDAPAttribute":["cn"],
        "uuidLDAPAttribute":["uidNumber"],
        "userObjectClasses":["inetOrgPerson, organizationalPerson"],
        "connectionUrl":["ldap://ldap_server:389"],
        "usersDn":["ou=TestUnit,dc=magenta,dc=test"],
        "authType":["simple"],
        "startTls":[],
        "bindDn":["cn=admin,dc=magenta,dc=test"],
        "bindCredential":["testMAG"],
        "customUserSearchFilter":[],
        "searchScope":["2"],
        "validatePasswordPolicy":["false"],
        "trustEmail":["false"],
        "useTruststoreSpi":["ldapsOnly"],
        "connectionPooling":["true"],
        "connectionPoolingAuthentication":[],
        "connectionPoolingDebug":[],
        "connectionPoolingInitSize":[],
        "connectionPoolingMaxSize":[],
        "connectionPoolingPrefSize":[],
        "connectionPoolingProtocol":[],
        "connectionPoolingTimeout":[],
        "connectionTimeout":[],
        "readTimeout":[],
        "pagination":["true"],
        "allowKerberosAuthentication":["false"],
        "serverPrincipal":[],
        "keyTab":[],
        "kerberosRealm":[],
        "debug":["false"],
        "useKerberosForPasswordAuthentication":["false"]
    }
}

ldap_json = '{"name":"ldap","providerId":"ldap","providerType":"org.keycloak.storage.UserStorageProvider","parentId":"os2datascanner","config":{"enabled":["true"],"priority":["0"],"fullSyncPeriod":["-1"],"changedSyncPeriod":["-1"],"cachePolicy":["DEFAULT"],"evictionDay":[],"evictionHour":[],"evictionMinute":[],"maxLifespan":[],"batchSizeForSync":["1000"],"editMode":["READ_ONLY"],"importEnabled":["true"],"syncRegistrations":["false"],"vendor":["other"],"usePasswordModifyExtendedOp":[],"usernameLDAPAttribute":["cn"],"rdnLDAPAttribute":["cn"],"uuidLDAPAttribute":["uidNumber"],"userObjectClasses":["inetOrgPerson, organizationalPerson"],"connectionUrl":["ldap://ldap_server:389"],"usersDn":["ou=TestUnit,dc=magenta,dc=test"],"authType":["simple"],"startTls":[],"bindDn":["cn=admin,dc=magenta,dc=test"],"bindCredential":["testMAG"],"customUserSearchFilter":[],"searchScope":["2"],"validatePasswordPolicy":["false"],"trustEmail":["false"],"useTruststoreSpi":["ldapsOnly"],"connectionPooling":["true"],"connectionPoolingAuthentication":[],"connectionPoolingDebug":[],"connectionPoolingInitSize":[],"connectionPoolingMaxSize":[],"connectionPoolingPrefSize":[],"connectionPoolingProtocol":[],"connectionPoolingTimeout":[],"connectionTimeout":[],"readTimeout":[],"pagination":["true"],"allowKerberosAuthentication":["false"],"serverPrincipal":[],"keyTab":[],"kerberosRealm":[],"debug":["false"],"useKerberosForPasswordAuthentication":["false"]}}'

str_payload = json.dumps(ldap_payload)

print(ldap_json)
print(str_payload)

print(str_payload == ldap_json)

SETUP_LDAP_URL = f'http://{SERVER}/auth/admin/realms/{REALM}/components'
r = requests.post(SETUP_LDAP_URL, data=str_payload, headers=headers2)
print(r.status_code, r.url)
print(r)

# Get list of clients

# USERS_URL = f'http://{SERVER}/auth/admin/realms/{REALM}/users'
# r = requests.get(USERS_URL, headers=headers)
# print(r.status_code, r.url)
# print(json.dumps(r.json(), indent=2))



