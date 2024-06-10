import smbc
import structlog
from traceback import print_exc

from django.conf import settings

from os2datascanner.utils.system_utilities import time_now

from os2datascanner.engine2.model.core import Handle
from os2datascanner.engine2.model.smbc import SMBCHandle

from os2datascanner.projects.grants.models.smbgrant import SMBGrant
from os2datascanner.projects.report.reportapp.models.documentreport import (
        DocumentReport)


logger = structlog.get_logger("reportapp")


def try_smb_delete_1(request, pks: list[int]) -> (bool, str):  # noqa: CCR001
    user = request.user

    if not settings.SMB_ALLOW_WRITE:
        logger.warning(
                "SMB deletion request with function disabled!",
                user=user)
        return (False, "function not enabled")

    # Find the referenced DocumentReport
    reports = DocumentReport.objects.filter(pk__in=pks)
    if not reports.exists():
        return (False, "DocumentReports not found")

    # Find the active user account
    account = user.account
    aliases = account.aliases
    organization = account.organization

    # Verify that the active user has an association to the DocumentReports
    illegal_reports = reports.exclude(alias_relation__in=aliases)
    if illegal_reports.exists():
        logger.warning(
                "SMB deletion request with no alias association!",
                user=user, aliases=illegal_reports.values_list("alias_relation", flat=True))
        return (False, "Account not associated with these DocumentReports")

    # Check that the DocumentReports represents a match (and not, for example,
    # an error message)

    if reports.exclude(number_of_matches__gte=1).exists():
        return (False, "DocumentReport does not identify a match")

    # Try to get credentials for the remote network drive
    try:
        grant: SMBGrant = SMBGrant.objects.get(
                organization__uuid=organization.uuid)
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
    for report in reports:
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
        except Exception as ex:
            print_exc()
            result = (False, f"unexpected error during deletion of report {report.pk}: {ex}")

    # Update the reports to indicate that the file is gone
    DocumentReport.objects.filter(pk__in=deleted_matches).update(
        resolution_status=DocumentReport.ResolutionChoices.REMOVED,
        resolution_time=time_now()
        )

    return result if result else (True, "ok")
