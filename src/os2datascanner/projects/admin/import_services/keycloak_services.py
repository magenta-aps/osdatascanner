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

import structlog
from django.conf import settings

from os2datascanner.utils.oauth2 import mint_cc_token
from os2datascanner.utils.token_caller import TokenCaller
from os2datascanner.engine2.utilities.backoff import WebRetrier

logger = structlog.get_logger("import_services")


def create_realm(realm_id: str):
    tc = TokenCaller(
            request_access_token,
            f"{settings.KEYCLOAK_BASE_URL}/auth/admin")
    return tc.post(
            "/realms",
            json={
                "enabled": True,
                # ID equal to name, as per Keycloak Server Admin process
                "id": realm_id,
                "realm": realm_id,
            })


def request_access_token():
    return mint_cc_token(
        f"{settings.KEYCLOAK_BASE_URL}/auth/realms/master/protocol/openid-connect/token",
        settings.KEYCLOAK_ADMIN_CLIENT, settings.KEYCLOAK_ADMIN_SECRET,
        wrapper=WebRetrier().run,
        post_timeout=settings.OAUTH2_TOKEN_TIMEOUT
    )


def request_create_component(realm, payload):
    return realm.make_caller().post(
            "/components",
            json=payload)


def request_update_component(realm, payload, component_id):
    return realm.make_caller().put(
            f"/components/{component_id}",
            json=payload)


def check_ldap_connection(connection_url, timeout=5):
    """ Given realm name, token and ldap connection url,
        returns a post request to testLDAPConnection for checking connection"""
    from os2datascanner.projects.admin.import_services.models import Realm
    return Realm(realm_id="master").make_caller().post(
            "/testLDAPConnection",
            json={
                "action": "testConnection",
                "connectionUrl": connection_url
            },
            timeout=timeout)


def check_ldap_authentication(
        connection_url, bind_dn, bind_credential, timeout=5):
    """ Given realm name, token, ldap connection url, bindDn and bindCredential,
            returns a post request to testLDAPConnection for checking authentication
            """
    from os2datascanner.projects.admin.import_services.models import Realm
    return Realm(realm_id="master").make_caller().post(
            "/testLDAPConnection",
            json={
                "action": "testAuthentication",
                "connectionUrl": connection_url,
                "bindCredential": bind_credential,
                "bindDn": bind_dn
            },
            timeout=timeout)


def sync_users(realm, provider_id, timeout=5):
    """Given a realm name and token, synchronises that realm's Keycloak users
    with the realm's identity provider."""
    return realm.make_caller().post(
            f"/user-storage/{provider_id}/sync?action=triggerFullSync",
            timeout=timeout)


def get_users(realm, timeout=5, max_elements=500, start_with=0):
    """Given a realm name and token, returns a list of maximum 500 users at a time
    known to Keycloak under that realm, starting with user 0."""
    return realm.make_caller().get(
            f"/users?first={start_with}&max={max_elements}")


def get_group_members(realm, group_id=None, timeout=5, max_elements=500, start_with=0):
    """Given a realm name, token and group-id, returns a list of maximum 500 members at a time
    known to Keycloak in that group, starting with user 0."""
    return realm.make_caller().get(
            f"/groups/{group_id}/members"
            f"?first={start_with}&max={max_elements}")


def get_groups(realm, timeout=5, max_elements=500, start_with=0):
    """Given a realm name and token, returns a list of maximum 500 groups at a time
    known to Keycloak under that realm, starting with group 0."""
    return realm.make_caller().get(
            f"/groups?first={start_with}&max={max_elements}"
            "&briefRepresentation=false")


def iter_api_call(realm, function, timeout=5, page_size=500, **kwargs):
    """Given a get_xxxx function, yields all results know to Keycloak,
    making as many API calls as necessary given the specified page size."""
    offset = 0

    while rq := function(
            realm,
            start_with=offset,
            timeout=timeout,
            max_elements=page_size,
            **kwargs):
        rq.raise_for_status()

        results = rq.json()
        if not results:  # No more elements to fetch
            break
        else:
            yield from results
            offset += len(results)


def iter_group_members(realm, group_id, group_dn=None, timeout=5, page_size=500):
    """Yields all members of given group, and saves the dn of the group as an attribute
    of the members"""

    for member in iter_api_call(realm, get_group_members, timeout=timeout,
                                page_size=page_size, group_id=group_id):
        member["attributes"]["group_dn"] = group_dn
        yield member


def iter_users(realm, timeout=5, page_size=500):
    """Yields all users known to Keycloak under the given realm."""
    yield from iter_api_call(realm, get_users, timeout=timeout, page_size=page_size)


def iter_groups(realm, timeout=5, page_size=500):
    """Yields all groups known to Keycloak under the given realm."""
    yield from iter_api_call(realm, get_groups, timeout=timeout, page_size=page_size)
