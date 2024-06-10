import smbc
import structlog
from traceback import print_exc

from django.conf import settings

from os2datascanner.engine2.model.core import Handle
from os2datascanner.engine2.model.smbc import SMBCHandle
from os2datascanner.engine2.pipeline import messages

from os2datascanner.projects.grants.models.smbgrant import SMBGrant
from os2datascanner.projects.report.reportapp.models.documentreport import (
        DocumentReport)


logger = structlog.get_logger("reportapp")


def try_smb_delete_1(request, path: str | None = None) -> (bool, str):
    user = request.user

    if not settings.SMB_ALLOW_WRITE:
        logger.warning(
                "SMB deletion request with function disabled!",
                user=user)
        return (False, "function not enabled")

    path = path if path else request.POST["path"]

    # Find the referenced DocumentReport
    try:
        report: DocumentReport = DocumentReport.objects.get(path=path)
    except DocumentReport.DoesNotExist:
        return (False, "DocumentReport not found")

    # Find the active user account
    account = user.account
    organization = account.organization

    # Verify that the active user has an association to the DocumentReport
    # TODO: This allows remediators to delete files they may not own. Intended?
    if not any(
            alias.account == account
            for alias in report.alias_relation.all()):
        logger.warning(
                "SMB deletion request with no alias association!",
                user=user, aliases=report.alias_relation.all())
        return (False, "Account not associated with this DocumentReport")

    # Check that the DocumentReport represents a match (and not, for example,
    # an error message)
    if report.matches:
        matches: messages.MatchesMessage = report.matches
    else:
        return (False, "DocumentReport does not identify a match")

    # Find the SMBCHandle object in this DocumentReport
    handle: Handle | None = None
    for handle in matches.handle.walk_up():
        if isinstance(handle, SMBCHandle):
            break
    else:
        logger.warning(
                "SMB deletion request for non-SMB resource!",
                user=user, handle=str(matches.handle))
        return (False, "target file is not on a Windows network drive")

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
    except Exception as ex:
        print_exc()
        return (False, f"unexpected error during deletion: {ex}")

    # Update the report to indicate that the file is gone
    report.resolution_status = DocumentReport.ResolutionChoices.REMOVED.value
    report.save()

    return (True, "ok")
