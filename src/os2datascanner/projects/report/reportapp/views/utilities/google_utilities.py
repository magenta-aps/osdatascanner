import json

import googleapiclient.errors
import structlog
from django.conf import settings
from google.oauth2 import service_account
from googleapiclient.discovery import build
from os2datascanner.projects.report.reportapp.models.documentreport import DocumentReport
from os2datascanner.projects.grants.models.googleapigrant import GoogleApiGrant
from os2datascanner.utils.system_utilities import time_now
from os2datascanner.projects.report.reportapp.views.utilities.msgraph_utilities import (
    get_handle_from_document_report)
from os2datascanner.engine2.model.gmail import GmailHandle

logger = structlog.get_logger("reportapp")


def gmail_deletion_service_account(account, google_grant):
    # Requires domain wide delegetion permission: https://www.googleapis.com/auth/gmail.modify
    # Add scope to: https://admin.google.com/ac/owl/domainwidedelegation
    SCOPES = ['https://www.googleapis.com/auth/gmail.modify']
    credentials = service_account.Credentials.from_service_account_info(
        json.loads(google_grant.service_account),
        scopes=SCOPES).with_subject(
        account.email
    )

    srvc_acc = build(serviceName='gmail', version='v1', credentials=credentials)
    return srvc_acc


def get_google_api_grant(org) -> (bool, GoogleApiGrant):
    try:
        grant = GoogleApiGrant.objects.get(organization=org)
        return (True, grant)
    except GoogleApiGrant.DoesNotExist:
        return (False, "no credentials available")
    except GoogleApiGrant.MultipleObjectsReturned:
        return (False, "too many credentials available")


def try_gmail_delete(request, pks: list[int]) -> (bool, str):  # noqa: CCR001
    user = request.user

    if not settings.GMAIL_ALLOW_WRITE:
        logger.warning(
            "Gmail deletion request with function disabled!",
            user=user)
        return (False, "function not enabled")

    reports = DocumentReport.objects.filter(pk__in=pks)
    if not reports.exists():
        return (False, "DocumentReports not found",)

    # Find the active user account
    account = user.account
    aliases = account.aliases.all()
    organization = account.organization

    # Verify that the active user has an association to the DocumentReports
    illegal_reports = reports.exclude(alias_relation__in=aliases)
    if illegal_reports.exists():
        logger.warning(
                "Gmail deletion request with no alias association!",
                user=user, aliases=illegal_reports.values_list("alias_relation", flat=True))
        return (False, "Account not associated with these DocumentReports")

    # Check that the DocumentReports represents a match (and not, for example,
    # an error message)
    if reports.exclude(number_of_matches__gte=1).exists():
        return (False, "DocumentReport does not identify a match")

    grant = None
    match get_google_api_grant(organization):
        case (True, g):
            grant = g
        case (False, str()) as failure:
            return failure

    srvc_acc = gmail_deletion_service_account(account, grant)

    deleted_matches: list[int] = []
    result: tuple | None = None
    for report in reports:
        try:
            message_handle = get_handle_from_document_report(report, GmailHandle)
            msg_id = message_handle.relative_path if message_handle else None
            srvc_acc.users().messages().trash(userId=account.email, id=msg_id).execute()
            deleted_matches.append(report.pk)

        except googleapiclient.errors.HttpError as http_error:
            if http_error.resp.status == 404:
                # Not found - it's gone
                deleted_matches.append(report.pk)
            else:
                logger.exception(f"unexpected HttpError during deletion of report {report.pk}",
                                 exc_info=True)

                result = (False, f"unexpected http error during deletion of report {report.pk}: "
                                 f"{http_error}")
        except Exception as ex:
            logger.exception(f"unexpected error during deletion of report {report.pk}",
                             exc_info=True)

            result = (False, f"unexpected error during deletion of report {report.pk}: {ex}")

    # Update the reports to indicate that the file is gone
    DocumentReport.objects.filter(pk__in=deleted_matches).update(
        resolution_status=DocumentReport.ResolutionChoices.REMOVED,
        resolution_time=time_now()
        )

    return result or (True, "ok")
