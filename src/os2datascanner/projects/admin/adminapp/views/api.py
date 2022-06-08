import json
from django.core.exceptions import ValidationError
from django.http import HttpResponse, JsonResponse
from django.utils.decorators import method_decorator
from django.views.generic import View
from django.views.decorators.csrf import csrf_exempt

from os2datascanner.engine2.rules.logical import OrRule
from ..models.rules.rule_model import Rule
from ..models.apikey_model import APIKey
from ..models.scannerjobs.scanner_model import Scanner
# from ..models.usererrorlog_model import UserErrorLog


def get_rule_1(key, body):
    """Returns the name and JSON representation of a rule."""

    pk = body.get("rule_id") if body else None
    if not isinstance(pk, int):
        return {
            "status": "fail",
            "message": "\"rule_id\" was missing or invalid"
        }

    try:
        rule = Rule.objects.select_subclasses().get(
                pk=pk, organization=key.organization)
    except Rule.DoesNotExist:
        return {
            "status": "fail",
            "message": "rule {0} does not exist".format(pk)
        }

    return {
        "status": "ok",
        "name": rule.name,
        "rule": rule.make_engine2_rule().to_json_object()
    }


def get_scanner_1(key, body):
    """Returns a summary of a scanner job: its name, the (censored) Sources
    that it will scan, and the rule that will be executed."""

    pk = body.get("scanner_id") if body else None
    if not isinstance(pk, int):
        return {
            "status": "fail",
            "message": "\"scanner_id\" was missing or invalid"
        }

    try:
        scanner = Scanner.objects.select_subclasses().get(
                pk=pk, organization=key.organization)
    except Scanner.DoesNotExist:
        return {
            "status": "fail",
            "message": "scanner {0} does not exist".format(pk)
        }

    rule_generator = (r.make_engine2_rule() for r in scanner.rules.all().select_subclasses())
    return {
        "status": "ok",
        "name": scanner.name,
        "rule": OrRule.make(*rule_generator).to_json_object(),
        "sources": list(s.censor().to_json_object()
                        for s in scanner.generate_sources())
    }


# def set_status_hidden(key, body):
#     """Retrieves a list of UserErrorLog id's and a handling-status value
#     from template.
#     Converts list to queryset and bulk_updates UserErrorLog model"""

#     error_pk = body.get("error_id")
#     status_value = body.get("new_status")
#     user_errors = UserErrorLog.objects.filter(pk__in=error_pk)

#     logger.info(
#         "User changing match status",
#         user=username,
#         status=UserErrorLog.ArchiveChoices(status_value),
#         **body,
#     )

#     if not user_errors.exists():
#         logger.warning(
#             "Could not find reports for status change",
#             user=username,
#             **body,
#         )
#         return {
#             "status": "fail",
#             "message": "unable to populate list of user errors"
#         }
#     for batch in iterate_queryset_in_batches(10000, user_errors):
#         for ue in batch:
#             if ue.archive_status is not None:
#                 return {
#                     "status": "fail",
#                     "message": "error {0} already has a status".format(ue.pk)
#                 }
#             else:
#                 ue.archive_status = status_value

#         UserErrorLog.objects.bulk_update(batch, ['archive_status'])
#         return {
#             "status": "ok"
#         }


def error_1(key, body):
    return {
        "status": "fail",
        "message": "path was missing or did not identify an endpoint"
    }


def catastrophe_1(key, body):
    return {
        "status": "fail",
        "message": "payload was not a valid JSON object"
    }


api_endpoints = {
    "get-rule/1": get_rule_1,
    "get-scanner/1": get_scanner_1,
    # "set-status-hidden": set_status_hidden
}


@method_decorator(csrf_exempt, name="dispatch")
class JSONAPIView(View):
    def post(self, request, *, path):
        key, error = self.test_key(request, path)
        if error:
            return error

        try:
            body = None
            if request.body:
                body = json.loads(request.body.decode("utf-8"))
            handler = api_endpoints.get(path, error_1)
        except json.JSONDecodeError:
            handler = catastrophe_1

        return JsonResponse(handler(key, body))

    def http_method_not_allowed(self, request, *, path):
        r = JsonResponse({
            "status": "fail",
            "message": "method not supported"
        })
        r.status_code = 405
        return r

    def test_key(self, request, path):
        auth = request.headers.get("authorization")
        if not auth:
            r = HttpResponse(status=401)
            r["WWW-Authentication"] = "Bearer realm=\"admin-api\""
            return None, r
        else:
            auth = auth.split()
            if not auth[0] == "Bearer" or len(auth) != 2:
                r = HttpResponse(status=400)
                r["WWW-Authentication"] = (
                        "Bearer realm=\"admin-api\" error=\"invalid_request\"")
                return None, r
            else:
                try:
                    key = APIKey.objects.get(uuid=auth[1])
                except (APIKey.DoesNotExist, ValidationError):
                    r = HttpResponse(status=401)
                    r["WWW-Authentication"] = (
                            "Bearer realm=\"admin-api\""
                            " error=\"invalid_token\"")
                    return None, r
                if path not in key:
                    r = HttpResponse(status=403)
                    r["WWW-Authentication"] = (
                            "Bearer realm=\"admin-api\""
                            " error=\"insufficient_scope\"")
                    return None, r
                else:
                    return key, None
