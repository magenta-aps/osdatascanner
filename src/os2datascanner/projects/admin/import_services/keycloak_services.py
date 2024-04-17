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
from os2datascanner.utils.oauth2 import mint_cc_token
from os2datascanner.engine2.utilities.backoff import WebRetrier

logger = structlog.get_logger("import_services")


def refresh_token(fn):
    """ Wrapper function, that on an HTTPError will try once to fetch a
    new access token, and run the function again. If it fails, HTTPError will be raised.
    It is required that 'token' is a keyword argument on the decorated function"""

    def _wrapper(*args, token, **kwargs):
        try:
            response = fn(*args, token=token, **kwargs)
            response.raise_for_status()
            return response
        except requests.exceptions.HTTPError as ex:
            logger.info(f"HTTPError {ex} ... fetching new token")
            token = request_access_token()
            response = fn(*args, token=token, **kwargs)
            response.raise_for_status()
            return response

    return _wrapper


# TODO: consider extending this to take list of requests and list of args
def get_token_first(request_function, realm, *args):
    """Utility function to retrieve access token before given API call

    Takes an API request function, a realm pk and the arguments for the given
    request call. Returns the error-response if token retrieval fails. Returns
    the response from the given request call otherwise.
    """
    token = request_access_token()
    return request_function(realm, token, *args)


# TODO: delete and replace usages with equivalent calls to get_token_first
def create_realm(realm):
    token = request_access_token()
    # TODO: add error-handling for unsuccessful requests (here or move all to views?)
    return request_create_new_realm(realm, token)


# TODO: delete and replace usages with equivalent calls to get_token_first
def add_ldap_conf(realm, payload):
    token = request_access_token()
    # TODO: add error-handling for unsuccessful requests (here or move all to views?)
    return request_create_component(realm, token, payload)


def request_create_new_realm(realm, token):
    """TODO:"""
    url = f'{settings.KEYCLOAK_BASE_URL}/auth/admin/realms'
    # TODO: consider defining headers as format string?
    headers = {
        'Authorization': f'bearer {token}',
        'Content-Type': 'application/json;charset=utf-8',
    }
    payload = {
        "enabled": True,
        "id": realm,  # ID equal to name, as per Keycloak Server Admin process
        "realm": realm,
    }
    return requests.post(url, data=json.dumps(payload), headers=headers)


def request_access_token():
    return mint_cc_token(
        f"{settings.KEYCLOAK_BASE_URL}/auth/realms/master/protocol/openid-connect/token",
        settings.KEYCLOAK_ADMIN_CLIENT, settings.KEYCLOAK_ADMIN_SECRET,
        wrapper=WebRetrier().run,
        post_timeout=settings.OAUTH2_TOKEN_TIMEOUT
    )


def request_create_component(realm, token, payload):
    """TODO:"""
    url = (settings.KEYCLOAK_BASE_URL +
           f'/auth/admin/realms/{realm}/components')
    headers = {
        'Authorization': f'bearer {token}',
        'Content-Type': 'application/json;charset=utf-8',
    }
    return requests.post(url, data=json.dumps(payload), headers=headers)


@refresh_token
def request_update_component(realm, payload, component_id, token=None):
    """TODO:"""
    url = (settings.KEYCLOAK_BASE_URL +
           f'/auth/admin/realms/{realm}/components/{component_id}')
    headers = {
        'Authorization': f'bearer {token}',
        'Content-Type': 'application/json;charset=utf-8',
    }

    return requests.put(url, data=json.dumps(payload), headers=headers)


def check_ldap_connection(realm, token, connection_url, timeout=5):
    """ Given realm name, token and ldap connection url,
        returns a post request to testLDAPConnection for checking connection"""

    url = (settings.KEYCLOAK_BASE_URL +
           f'/auth/admin/realms/{realm}/testLDAPConnection')

    headers = {
        'Authorization': f'bearer {token}',
        'Content-Type': 'application/json;charset=utf-8',
    }
    payload = {
        "action": "testConnection",
        "connectionUrl": connection_url
    }
    data = json.dumps(payload)
    return requests.post(url, data=data, headers=headers, timeout=timeout)


def check_ldap_authentication(realm, token, connection_url,
                              bind_dn, bind_credential, timeout=5):
    """ Given realm name, token, ldap connection url, bindDn and bindCredential,
            returns a post request to testLDAPConnection for checking authentication
            """

    url = (settings.KEYCLOAK_BASE_URL +
           f'/auth/admin/realms/{realm}/testLDAPConnection')

    headers = {
        'Authorization': f'bearer {token}',
        'Content-Type': 'application/json;charset=utf-8',
    }
    payload = {
        "action": "testAuthentication",
        "connectionUrl": connection_url,
        "bindCredential": bind_credential,
        "bindDn": bind_dn
    }
    data = json.dumps(payload)
    return requests.post(url, data=data, headers=headers, timeout=timeout)


@refresh_token
def sync_users(realm, provider_id, token=None, timeout=5):
    """Given a realm name and token, synchronises that realm's Keycloak users
    with the realm's identity provider."""

    headers = {
        'Authorization': f'bearer {token}'
    }
    url = (settings.KEYCLOAK_BASE_URL +
           f'/auth/admin/realms/{realm}/user-storage/{provider_id}'
           '/sync?action=triggerFullSync')
    return requests.post(url, headers=headers, timeout=timeout)


@refresh_token
def get_users(realm, timeout=5, max_elements=500, start_with=0, token=None):
    """Given a realm name and token, returns a list of maximum 500 users at a time
    known to Keycloak under that realm, starting with user 0."""

    headers = {
        'Authorization': f'bearer {token}'
    }
    url = (settings.KEYCLOAK_BASE_URL +
           f'/auth/admin/realms/{realm}/users?first={start_with}&max='
           f'{max_elements}')
    return requests.get(url, headers=headers, timeout=timeout)


@refresh_token
def get_group_members(realm, group_id=None, timeout=5, max_elements=500, start_with=0, token=None):
    """Given a realm name, token and group-id, returns a list of maximum 500 members at a time
    known to Keycloak in that group, starting with user 0."""
    headers = {
        'Authorization': f'bearer {token}'
    }
    url = (settings.KEYCLOAK_BASE_URL +
           f'/auth/admin/realms/{realm}/groups/{group_id}/members?first={start_with}&max='
           f'{max_elements}')
    return requests.get(url, headers=headers, timeout=timeout)


@refresh_token
def get_groups(realm, timeout=5, max_elements=500, start_with=0, token=None):
    """Given a realm name and token, returns a list of maximum 500 groups at a time
    known to Keycloak under that realm, starting with group 0."""

    headers = {
        'Authorization': f'bearer {token}'
    }
    url = (settings.KEYCLOAK_BASE_URL +
           f'/auth/admin/realms/{realm}/groups?first={start_with}&max='
           f'{max_elements}&briefRepresentation=false')
    return requests.get(url, headers=headers, timeout=timeout)


def iter_api_call(realm, function, token=None, timeout=5, page_size=500, **kwargs):
    """Given a get_xxxx function, yields all results know to Keycloak,
    makins as many API calls as necessary given the specified page size."""
    offset = 0

    while rq := function(
            realm,
            start_with=offset,
            token=token,
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


def iter_group_members(realm, group_id, group_dn=None, token=None, timeout=5, page_size=500):
    """Yields all members of given group,
    and saves the dn of the group as an attribute of the members"""

    for member in iter_api_call(realm, get_group_members, token=token, timeout=timeout,
                                page_size=page_size, group_id=group_id):
        member["attributes"]["group_dn"] = group_dn
        yield member


def iter_users(realm, token=None, timeout=5, page_size=500):
    """Yields all users known to Keycloak under the given realm."""
    yield from iter_api_call(realm, get_users, token=token, timeout=timeout, page_size=page_size)


def iter_groups(realm, token=None, timeout=5, page_size=500):
    """Yields all groups known to Keycloak under the given realm."""
    yield from iter_api_call(realm, get_groups, token=token, timeout=timeout, page_size=page_size)
