# Part of the OSdatascanner system, copyright © 2014-2026 Magenta ApS.
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, you can
# obtain one at http://mozilla.org/MPL/2.0/.

import smbc
import structlog

from os2datascanner.utils.system_utilities import time_now

from os2datascanner.engine2.model.core import Handle
from os2datascanner.engine2.model.smbc import SMBCHandle

from os2datascanner.projects.grants.models.smbgrant import SMBGrant
from os2datascanner.projects.report.reportapp.models.documentreport import (
        DocumentReport)
from .document_report_utilities import validate_delete_request, DeleteRequestError


logger = structlog.get_logger("reportapp")


def try_smb_delete_1(request, pks: list[int]) -> (bool, str):  # noqa: CCR001
    user = request.user

    if not user.account.organization.has_smb_file_delete_permission():
        logger.warning("SMB deletion request with function disabled!", user=user)
        return (False, "function not enabled")

    try:
        validate_delete_request(user, pks)
    except DeleteRequestError as e:
        return (False, str(e))

    # Try to get credentials for the remote network drive
    try:
        grant: SMBGrant = SMBGrant.objects.get(
                organization__uuid=user.account.organization.uuid)
    except SMBGrant.DoesNotExist:
        return (False, "no credentials available")
    except SMBGrant.MultipleObjectsReturned:
        return (False, "too many credentials available")

    def __magic_auth_handler(*args):
        # The positional args to this function are used by pysmbc to specify
        # hints for the various authentication parameters, but we don't care
        # about them -- the grant tells us everything we need to know
        return (grant.domain, grant.username, grant.password)

    deleted_matches: list[int] = []
    result: tuple | None = None
    for report in DocumentReport.objects.filter(pk__in=pks):
        # Find the SMBCHandle object in this DocumentReport
        handle: Handle | None = None
        for handle in report.matches.handle.walk_up():
            if isinstance(handle, SMBCHandle):
                break
        else:
            logger.warning(
                    "SMB deletion request for non-SMB resource!",
                    user=user, handle=str(report.matches.handle))
            return (False, "target file is not on a Windows network drive")

        # Get a smb:// URL to the file we've discovered (without authentication
        # details)...
        smb_url = handle.source._to_url() + "/" + handle.relative_path
        # ... and get a libsmbclient context object (with authentication) for
        # making SMB RPC calls
        smb_ctx = smbc.Context(auth_fn=__magic_auth_handler)

        # Try to delete the file
        try:
            logger.info(
                    "attempting to delete SMB resource",
                    user=user, smb_url=smb_url)
            smb_ctx.unlink(smb_url)
            deleted_matches.append(report.pk)
        except smbc.NoEntryError:
            # We tried to delete this, but it was already gone...? Oh well,
            # let's just declare victory
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
