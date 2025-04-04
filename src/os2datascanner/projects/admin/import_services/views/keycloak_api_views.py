from requests.exceptions import ReadTimeout
import structlog

from django.http import JsonResponse

from ..keycloak_services import check_ldap_connection
from ..keycloak_services import check_ldap_authentication


logger = structlog.get_logger("keycloak_api_views")


def process_request(request, parameter_keys, kc_call):
    parameters = []
    missing_parameters = []
    for key in parameter_keys:
        parameter = request.POST.get(key, None)
        if parameter:
            parameters.append(parameter)
        else:
            missing_parameters.append(key)
    if missing_parameters:
        error = "parameters missing: {keys}".format(keys=missing_parameters)
        return JsonResponse(
            {'errorMessage': error}, status=400
        )
    status = 400
    json_data = {'errorMessage': "LDAP test error"}
    try:
        check_response = kc_call(*parameters, timeout=0.4)
        if check_response.status_code == 204:
            status = 200
            json_data = {'successMessage': "LDAP test success"}
        else:
            status = check_response.status_code
            json_data = check_response.json()
    except ReadTimeout:
        status = 408
        json_data['errorMessage'] = "Keycloak: no response"
    except BaseException:
        logger.exception("LDAP connection test raised unexpected error")
    finally:
        return JsonResponse(json_data, status=status)  # noqa: B012,
        # return inside finally blocks cause exceptions to be silenced


def verify_connection(request):
    return process_request(request, ['url'], check_ldap_connection)


def verify_authentication(request):
    return process_request(
        request,
        ['url', 'bind_dn', 'bind_credential'],
        check_ldap_authentication,
    )
