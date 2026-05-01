# Part of the OSdatascanner system, copyright © 2014-2026 Magenta ApS.
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, you can
# obtain one at http://mozilla.org/MPL/2.0/.

import structlog
from exchangelib import Message
from exchangelib.errors import ErrorItemNotFound

from os2datascanner.utils.system_utilities import time_now

from os2datascanner.engine2.model.core import Handle
from os2datascanner.engine2.model.ews import EWSMailHandle, EWSMailResource

from os2datascanner.projects.grants.models.ewsgrant import EWSGrant
from os2datascanner.projects.grants.models.graphgrant import GraphGrant
from os2datascanner.projects.report.reportapp.models.documentreport import (
        DocumentReport)

from os2datascanner.engine2.model.core import SourceManager
from .document_report_utilities import validate_delete_request, DeleteRequestError

logger = structlog.get_logger("reportapp")


def find_exchange_grant(org) -> (bool, EWSGrant | GraphGrant | str):  # noqa CCR001
    # Try to get credentials, prefer EWSGrant if available (but prefer an
    # GraphGrant /with/ a client secret over a EWSGrant /without/ a password)
    # unless GraphGrant is prioritized by the organization
    grant: GraphGrant | EWSGrant | None = None

    def pick_grant(grant_type, credential_attr):
        for candidate in grant_type.objects.filter(organization=org):

            nonlocal grant

            if getattr(candidate, credential_attr):
                if grant:
                    return (False, "too many credentials available")
                else:
                    grant = candidate
            else:
                logger.warning(
                        f"skipping grant candidate with empty {credential_attr}",
                        candidate=candidate
                )
        return True, None

    if org.prioritize_graphgrant:
        valid, error = pick_grant(GraphGrant, "client_secret")
        if not valid:
            return False, error

    else:
        valid, error = pick_grant(EWSGrant, "password")
        if not valid:
            return False, error
        if not grant:
            valid, error = pick_grant(GraphGrant, "client_secret")
            if not valid:
                return False, error

    if grant:
        return (True, grant)
    else:
        return (False, "no credentials available")


def try_ews_delete(request, pks: list[int]) -> (bool, str):  # noqa: C901, CCR001 too complex
    user = request.user

    if not user.account.organization.has_exchange_email_delete_permission():
        logger.warning("EWS deletion request with function disabled!", user=user)
        return (False, "function not enabled")

    try:
        validate_delete_request(user, pks)
    except DeleteRequestError as e:
        return (False, str(e))

    grant = None
    match find_exchange_grant(user.account.organization):
        case (True, g):
            grant = g
        case (False, str()) as failure:
            return failure

    def get_ews_resource(grant, handle: EWSMailHandle) -> EWSMailResource:
        sm = SourceManager()
        # Note: this isn't well-suited for remap()
        # because we need to manually copy too much from the original source
        if isinstance(grant, GraphGrant):
            handle.source._client_id = grant.app_id
            handle.source._tenant_id = grant.tenant_id
            handle.source._client_secret = grant.client_secret
            return handle.follow(sm)

        elif isinstance(grant, EWSGrant):
            handle.source._admin_user = grant.username
            handle.source._admin_password = grant.password
            return handle.follow(sm)

        else:
            raise ValueError(f"Expected either an EWSGrant or GraphGrant! not {grant}")

    deleted_matches: list[int] = []
    result: tuple | None = None
    for report in DocumentReport.objects.filter(pk__in=pks):
        # Find the EWSMailHandle
        handle: Handle | None = None
        for h in report.matches.handle.walk_up():
            if isinstance(h, EWSMailHandle):
                handle = h
                break
        else:
            logger.warning(
                    "EWS deletion request for non-ews resource!",
                    user=user, handle=str(report.matches.handle))
            return (False, "target is not connected to an Exchange account!")

        try:
            rsrc = get_ews_resource(grant, handle)

            # We need the message_id and an exchangelib Account
            _, message_id = rsrc._ids
            ews_account = rsrc._get_cookie()

            logger.info(
                "attempting to delete EWS resource",
                user=user, report=report
            )

            # Providing 'account' keyword to Message allows use of delete methods.
            # Soft delete moves mails to trash's "Recoverable items".
            Message(account=ews_account, id=message_id).soft_delete()
            deleted_matches.append(report.pk)

        # Prone to expansion:
        # Hard to know in advance, but there _might_ be more exceptions meaning something is
        # deleted.
        except ErrorItemNotFound:
            # It's already gone
            deleted_matches.append(report.pk)
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
