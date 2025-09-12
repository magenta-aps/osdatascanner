import requests
import structlog
from django.utils.translation import gettext as _
from django.core.exceptions import PermissionDenied
from os2datascanner.engine2.model.core import Handle
from os2datascanner.engine2.model.msgraph import MSGraphMailMessageHandle
from os2datascanner.engine2.model.msgraph.files import MSGraphFileHandle
from os2datascanner.engine2.model.msgraph.utilities import MSGraphSource
from os2datascanner.projects.grants.models.graphgrant import GraphGrant
from os2datascanner.projects.report.organizations.models import Account
from os2datascanner.core_organizational_structure.models.aliases import AliasType

logger = structlog.get_logger("reportapp")

# Consider moving GraphCaller out of MSGraphSource.
GraphCaller = MSGraphSource.GraphCaller


def outlook_settings_from_owner(owner: str):
    """Returns the AccountOutlookSetting object related to a specific owner."""
    from ....organizations.models import AccountOutlookSetting
    try:
        return AccountOutlookSetting.objects.get(account__email=owner)
    except AccountOutlookSetting.DoesNotExist:
        logger.warning(f"Could not find AccountOutlookSetting for owner {owner}")
        return None


def check_msgraph_grant(org) -> GraphGrant | PermissionDenied:
    try:
        return GraphGrant.objects.get(organization=org)
    except GraphGrant.DoesNotExist:
        message = _(
            "Your organization is missing a valid MSGraph grant."
        )
        logger.warning(message)
        raise PermissionDenied(message)
    except GraphGrant.MultipleObjectsReturned:
        message = _(
            "Unexpected error: More than one MSGraph grant was found for your organization."
        )
        logger.warning(message)
        raise PermissionDenied(message)


def categorize_email_from_report(document_report,
                                 category_name: str,
                                 gc: GraphCaller):
    """
    Adds category to a specific email retrieved from a DocumentReport.
    Requires Mail.ReadWrite
    """

    # Return early scenarios
    check_msgraph_grant(document_report.scanner_job.organization)
    if not document_report.scanner_job.organization.has_categorize_permission():
        org_permission_message = _("Your organization does not allow this operation.")
        logger.warning(org_permission_message)
        raise PermissionDenied(org_permission_message)

    # Fetch what categories are already set on this email.
    email_categories = get_msgraph_mail_categories_from_document_report(document_report)

    # Make sure an OS2datascanner category isn't already added.
    # We don't want to mark False Positive marked ones with Match, or
    # mark any mails twice.
    owner = document_report.owner
    if settings := outlook_settings_from_owner(owner):
        if not any(
                    category.category_name in email_categories
                for category in settings.outlook_categories.all()):
            # Append OS2datascanner category
            email_categories.append(category_name)

    message_handle = get_handle_from_document_report(document_report, MSGraphMailMessageHandle)
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
        logger.warning("Couldn't categorize email!", exc_info=ex)


def delete_email(document_report, account: Account):
    """ Deletes an email through the MSGraph API and handles DocumentReport accordingly.
    Retrieves a new access token if not provided one."""
    from os2datascanner.projects.report.reportapp.models.documentreport import DocumentReport
    from os2datascanner.projects.report.reportapp.views.utilities.document_report_utilities \
        import is_owner, handle_report

    # Return early scenarios
    graph_grant = check_msgraph_grant(account.organization)
    if not account.organization.has_msgraph_email_delete_permission():
        allow_deletion_message = _("System configuration does not allow mail deletion.")
        logger.warning(allow_deletion_message)
        raise PermissionDenied(allow_deletion_message)

    owner = document_report.owner

    if not is_owner(owner, account):
        logger.warning(f"User {account} tried to delete an email belonging to {owner}!")
        not_owner_message = (_("Not allowed! You tried to delete an email belonging to {owner}!").
                             format(owner=owner))
        raise PermissionDenied(not_owner_message)

    # Open a session and start doing stuff
    with requests.Session() as session:
        gc = GraphCaller(
            graph_grant.make_token,
            session)

        message_handle = get_handle_from_document_report(document_report, MSGraphMailMessageHandle)
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
                logger.warning("Couldn't delete email!", exc_info=ex)
                # PermissionDenied is a bit misleading here, it may not represent what went wrong.
                # But sticking to this exception, makes handling it in the view easier.
                raise PermissionDenied(delete_failed_message)


def get_handle_from_document_report(document_report, handle_type) -> Handle:
    """ Walks up a DocumentReport's metadata chain to return provided handle type or None. """
    # Look to grab the handle that represents the email (to support matches in attachments)
    message_handle = next(
        (handle for handle in document_report.metadata.handle.walk_up()
         if isinstance(handle, handle_type)), None)
    return message_handle


def get_msgraph_mail_document_reports(account):
    from os2datascanner.projects.report.reportapp.models.documentreport import DocumentReport
    # TODO: Should this return only unresolved reports?
    # When used for trying to get a tenant id, it lowers our odds of getting one.
    # On the other hand, it might be annoying for the user to have an email cateogorized
    # if they've already handled the result in OS2datascanner.
    document_report = DocumentReport.objects.filter(
        alias_relations__account=account,
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


def delete_file(document_report, account: Account):
    from os2datascanner.projects.report.reportapp.models.documentreport import DocumentReport
    from os2datascanner.projects.report.reportapp.views.utilities.document_report_utilities \
        import is_owner, handle_report

    # Return early scenarios
    graph_grant = check_msgraph_grant(account.organization)
    if not account.organization.has_msgraph_file_delete_permission():
        allow_deletion_message = _("System configuration does not allow file deletion.")
        logger.warning(allow_deletion_message)
        raise PermissionDenied(allow_deletion_message)

    owner = document_report.owner

    if (not is_owner(owner, account) and
            not account.aliases.filter(_alias_type=AliasType.REMEDIATOR)):
        logger.warning(f"User {account} tried to delete a file belonging to {owner}!")
        not_owner_message = (_("Not allowed! You tried to delete a file belonging to {owner}!").
                             format(owner=owner))
        raise PermissionDenied(not_owner_message)

    with requests.Session() as session:
        gc = GraphCaller(graph_grant.make_token, session)

        file_handle = get_handle_from_document_report(document_report, MSGraphFileHandle)
        item_path = file_handle.relative_path

        try:
            delete_response = gc.delete_file(owner, item_path)

            if delete_response.ok:
                logger.info(f"Successfully deleted file on behalf of {account}! "
                            f"Setting resolution status REMOVED")
                handle_report(account,
                              document_report=document_report,
                              action=DocumentReport.ResolutionChoices.REMOVED)
        except requests.HTTPError as ex:
            # If the file is deleted from Outlook but a user clicks delete on the reportmodule
            # It will still be handled as deleted.
            if ex.response.status_code in (404, 410):
                handle_report(account,
                              document_report=document_report,
                              action=DocumentReport.ResolutionChoices.REMOVED)
                logger.info(f"Delete mail got response code {ex.response.status_code}! "
                            "Interpreted as file deleted - Document report handled as deleted")

            else:
                delete_failed_message = _("Couldn't delete file! Code: {status_code}").format(
                    status_code=ex.response.status_code)
                logger.warning(f"Couldn't delete file! Got response: {ex.response}")
                # PermissionDenied is a bit misleading here, it may not represent what went wrong.
                # But sticking to this exception, makes handling it in the view easier.
                raise PermissionDenied(delete_failed_message)
