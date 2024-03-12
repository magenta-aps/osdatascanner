from enum import Enum

import requests
import structlog
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.core.exceptions import PermissionDenied

from os2datascanner.engine2.model.msgraph import MSGraphMailMessageHandle
from os2datascanner.engine2.model.msgraph.utilities import make_token, MSGraphSource
from os2datascanner.projects.report.organizations.models import Account

from os2datascanner.core_organizational_structure.models import OutlookCategorizeChoices

logger = structlog.get_logger()

# Consider moving GraphCaller out of MSGraphSource.
GraphCaller = MSGraphSource.GraphCaller


class OutlookCategoryName(Enum):
    """ Enum used to set Outlook category names """
    # Don't translate these - it'll give you proxy objects which aren't serializable,
    # and we need to be able to trust their values.
    # TODO: We need to rename these to reflect the new name "OSdatascanner"
    # but this will break functionality with the customers already using it.
    Match = "OS2datascanner Match"
    FalsePositive = "OS2datascanner False Positive"


def check_msgraph_settings():
    if (not settings.MSGRAPH_APP_ID
            or not settings.MSGRAPH_CLIENT_SECRET
            or not settings.MSGRAPH_ALLOW_WRITE):
        msgraph_app_settings_message = _("System configuration is missing"
                                         " Azure-application credentials. ")
        logger.warning(msgraph_app_settings_message)
        raise PermissionDenied(msgraph_app_settings_message)


def categorize_email_from_report(document_report,
                                 category_name: str,
                                 gc: GraphCaller):
    """
    Adds category to a specific email retrieved from a DocumentReport.
    Requires Mail.ReadWrite
    """

    # Return early scenarios
    check_msgraph_settings()
    required_permissions = (OutlookCategorizeChoices.ORG_LEVEL,
                            OutlookCategorizeChoices.INDIVIDUAL_LEVEL)
    if document_report.organization.outlook_categorize_email_permission not in required_permissions:
        org_permission_message = _("Your organization does not allow this operation.")
        logger.warning(org_permission_message)
        raise PermissionDenied(org_permission_message)

    # Fetch what categories are already set on this email.
    email_categories = get_msgraph_mail_categories_from_document_report(document_report)

    # Make sure an OS2datascanner category isn't already added.
    # We don't want to mark False Positive marked ones with Match, or
    # mark any mails twice.
    if not any(category.value in email_categories for category in OutlookCategoryName):
        # Append OS2datascanner category
        email_categories.append(category_name)

    owner = document_report.owner
    message_handle = get_mail_message_handle_from_document_report(document_report)
    msg_id = message_handle.relative_path if message_handle else None

    try:
        categorize_email_response = gc.categorize_mail(owner,
                                                       msg_id,
                                                       email_categories)
        if categorize_email_response.ok:
            logger.info(f"Successfully added category {category_name} "
                        f"to email: {document_report}!")

    except requests.HTTPError as ex:
        # We don't want to raise anything here
        # The most likely scenario is just that the mail doesn't exist anymore.
        logger.warning(f"Couldn't categorize email! Got response: {ex.response}")


def delete_email(document_report, account: Account):
    """ Deletes an email through the MSGraph API and handles DocumentReport accordingly.
    Retrieves a new access token if not provided one."""
    from os2datascanner.projects.report.reportapp.models.documentreport import DocumentReport
    from os2datascanner.projects.report.reportapp.views.utilities.document_report_utilities \
        import is_owner, handle_report

    def _make_token():
        return make_token(
            settings.MSGRAPH_APP_ID,
            tenant_id,
            settings.MSGRAPH_CLIENT_SECRET)

    # Return early scenarios
    check_msgraph_settings()
    if not account.organization.has_delete_permission():
        allow_deletion_message = _("System configuration does not allow mail deletion.")
        logger.warning(allow_deletion_message)
        raise PermissionDenied(allow_deletion_message)

    owner = document_report.owner

    if not is_owner(owner, account):
        logger.warning(f"User {account} tried to delete an email belonging to {owner}!")
        not_owner_message = (_("Not allowed! You tried to delete an email belonging to {owner}!").
                             format(owner=owner))
        raise PermissionDenied(not_owner_message)

    tenant_id = get_tenant_id_from_document_report(document_report)

    # Open a session and start doing stuff
    with requests.Session() as session:
        gc = GraphCaller(
            _make_token,
            session)

        message_handle = get_mail_message_handle_from_document_report(document_report)
        msg_id = message_handle.relative_path if message_handle else None

        try:
            delete_response = gc.delete_message(owner, msg_id)

            if delete_response.ok:
                logger.info(f"Successfully deleted email on behalf of {account}! "
                            "Settings resolution status REMOVED")

                handle_report(account,
                              document_report=document_report,
                              action=DocumentReport.ResolutionChoices.REMOVED)
        except requests.HTTPError as ex:
            # If the email is deleted from Outlook but a user clicks delete on the reportmodule
            # It will still be handled as deleted.
            if ex.response.status_code in (404, 410):
                from os2datascanner.projects.report.reportapp.models.documentreport import \
                    DocumentReport
                handle_report(account,
                              document_report=document_report,
                              action=DocumentReport.ResolutionChoices.REMOVED)
                logger.info(f"Delete mail got response code {ex.response.status_code}! "
                            "Interpreted as mail deleted - Document report handled as deleted")

            else:
                delete_failed_message = _("Couldn't delete email! Code: {status_code}").format(
                    status_code=ex.response.status_code)
                logger.warning(f"Couldn't delete email! Got response: {ex.response}")
                # PermissionDenied is a bit misleading here, it may not represent what went wrong.
                # But sticking to this exception, makes handling it in the view easier.
                raise PermissionDenied(delete_failed_message)


def get_mail_message_handle_from_document_report(document_report) \
        -> MSGraphMailMessageHandle or None:
    """ Walks up a DocumentReport's metadata chain to return MSGraphMailMessageHandle
    or None. """
    # Look to grab the handle that represents the email (to support matches in attachments)
    message_handle = next(
        (handle for handle in document_report.metadata.handle.walk_up()
         if isinstance(handle, MSGraphMailMessageHandle)), None)
    return message_handle


def get_tenant_id_from_document_report(document_report) -> str or PermissionDenied:
    tenant_id = None
    # tenant_id isn't censored in metadata, which means we can grab it from there.
    for handle in document_report.metadata.handle.walk_up():
        if isinstance(handle.source, MSGraphSource):
            # we might want to add an accessor for this to avoid the private member
            tenant_id = handle.source._tenant_id
            return tenant_id
    if not tenant_id:
        logger.warning(f"Could not retrieve any tenant id from {document_report}")
        no_tenant_message = _("Could not find your Microsoft tenant!")
        # PermissionDenied is a bit misleading here, as it may not represent what went wrong.
        # But sticking to this exception, makes handling it in the view easier.
        raise PermissionDenied(no_tenant_message)


def get_msgraph_mail_document_reports(account):
    from os2datascanner.projects.report.reportapp.models.documentreport import DocumentReport
    # TODO: Should this return only unresolved reports?
    # When used for trying to get a tenant id, it lowers our odds of getting one.
    # On the other hand, it might be annoying for the user to have an email cateogorized
    # if they've already handled the result in OS2datascanner.
    document_report = DocumentReport.objects.filter(
        alias_relation__account=account,
        source_type="msgraph-mail",
        number_of_matches__gte=1)
    if not document_report:
        logger.warning("Found no MSGraph mail DocumentReports.")
        no_dr_message = _("You currently have no Outlook reports. Can't create categories!")
        # PermissionDenied is a bit misleading here, as it may not represent what went wrong.
        # But sticking to this exception, makes handling it in the view easier.
        raise PermissionDenied(no_dr_message)
    return document_report


def get_msgraph_mail_categories_from_document_report(document_report) -> list:
    return document_report.metadata.metadata.get("outlook-categories", [])
