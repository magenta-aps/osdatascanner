import structlog
from abc import ABC, abstractmethod
from typing import Iterator

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template import loader
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from more_itertools.more import peekable

from .models.scannerjobs.scanner import Scanner, ScanStatus
from .models.usererrorlog import UserErrorLog

from os2datascanner.utils.template_utilities import (
        get_localised_template_names)

logger = structlog.get_logger("adminapp")


class NotificationEmail(ABC):

    def get_txt_templates(self):
        return loader.select_template(
            get_localised_template_names([self.txt_template_name]))

    def get_html_templates(self):
        return loader.select_template(
            get_localised_template_names([self.html_template_name]))

    def notify(self) -> None:
        # get_users returns an iterator (most cases a generator), which means we
        # can't do a simple check of truthiness, but neither may we consume from it.
        # Use more-itertools peek to check next() value without consuming,
        # returning None as default instead of StopIteration.
        users = peekable(self.get_users())

        if not users.peek(None):
            logger.warning("get_users() returned no users! No email notifications will be sent.")
            return

        for user in users:
            context = self.create_context(user)
            logger.info("Created context for info mail", context=context, for_user=user)
            msg = create_msg(context, self.subject, user.email,
                             self.get_txt_templates(), self.get_html_templates())
            send_msg(msg)

    @abstractmethod
    def create_context(self, user, *args, **kwargs) -> dict:
        """Method to prepare context for generating a message."""

    @abstractmethod
    def get_users(self, *args, **kwargs) -> Iterator[str]:
        """Method for getting the recipients of the notification."""

    @property
    @abstractmethod
    def txt_template_name(self) -> str:
        """The name of the .txt template file."""

    @property
    @abstractmethod
    def html_template_name(self) -> str:
        """The name of the .html template file."""

    @property
    @abstractmethod
    def subject(self) -> str:
        """The subject of the notification email."""


class FinishedScannerNotificationEmail(NotificationEmail):
    """
    Send a mail to scannerjob responsible when a scannerjob has finished.
    """

    txt_template_name = "mail/finished_scannerjob.txt"
    html_template_name = "mail/finished_scannerjob.html"
    subject = _("Your OSdatascanner scan is finished.")

    def __init__(self, scanner: Scanner, scan_status: ScanStatus,
                 *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scanner = scanner
        self.status = scan_status

    def get_users(self) -> Iterator[str]:
        for user in self.scanner.contacts.iterator():
            email = user.email

            if email:
                yield user
            else:
                logger.info("No email found for user while trying to notify of completed "
                            "scan. No email notification sent!", for_user=user)

    def create_context(self, user, *args, **kwargs) -> dict:
        """
        Creates a context dict for the finished scannerjob ready for rendering.
        """
        user_logs = UserErrorLog.objects.filter(
            scan_status=self.status).count()
        context = {
            "admin_login_url": settings.SITE_URL,
            "institution": settings.NOTIFICATION_INSTITUTION,
            "full_name": user.get_full_name() or user.username if user else "",
            "total_objects": self.status.total_objects,
            "scanner_name": self.scanner.name,
            "object_size": self.status.scanned_size,
            "completion_time": get_scanner_time(self.status),
            "usererrorlogs": user_logs,
            "object_plural": self.scanner.as_subclass().object_name_plural,
        }

        return context


class InvalidScannerNotificationEmail(NotificationEmail):
    """
    Send a mail to whomever is responsible for the scanner when a scanner was not automatically
    executed due to its validation status.
    """

    txt_template_name = "mail/invalid_scannerjob.txt"
    html_template_name = "mail/invalid_scannerjob.html"
    subject = _("OSdatascanner could not execute the scan.")

    def __init__(self, scanner: Scanner, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scanner = scanner

    def get_users(self) -> Iterator[str]:
        for user in self.scanner.contacts.iterator():
            email = user.email

            if email:
                yield user
            else:
                logger.info("No email found for user while trying to notify of invalid "
                            "scan. No email notification sent!", for_user=user)

    def create_context(self, *args, **kwargs) -> dict:
        """
        Creates a context dict for the invalid scannerjob ready for rendering.
        """
        context = {
            "institution": settings.NOTIFICATION_INSTITUTION,
            "scanner_name": self.scanner.name,
            # We need to remove the trailing slash from the site url
            "scanner_edit_url": settings.SITE_URL[:-1] + self.scanner.get_update_url()
        }

        return context


class GraphGrantExpiryNotificationEmail(NotificationEmail):
    """
    Send a mail to whomever is responsible for the Graph Grant when their secret is about to expire.
    """

    txt_template_name = "mail/grant_expiry.txt"
    html_template_name = "mail/grant_expiry.html"
    subject = _("Your GraphGrant needs to be updated.")

    def __init__(self, grant, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.grant = grant

    def get_users(self):
        for user in self.grant.contacts.iterator():
            if user.email:
                yield user
            else:
                logger.info("No email found for user while trying to notify of grant "
                            "expiration. No email notification sent!", for_user=user)

    def create_context(self, user, *args, **kwargs) -> dict:
        return {
            "institution": settings.NOTIFICATION_INSTITUTION,
            "tenant": self.grant.tenant_id,
            "expiry_date": self.grant.expiry_date,
            "grant_edit_url": settings.SITE_URL[:-1] +
            reverse('msgraphgrant-update',
                    kwargs={'pk': self.grant.uuid}),
        }


def get_scanner_time(scan_status: ScanStatus):
    """
    Calculates and formats the total runtime for the scannerjob.
    """
    total_time = scan_status.last_modified - scan_status.start_time

    hours = round(total_time.total_seconds() // 3600)
    minutes = round((total_time.total_seconds() % 3600) // 60)
    seconds = round((total_time.total_seconds() % 3600) % 60)

    return str(hours) + "t" + str(minutes) + "m" + str(seconds) + "s"


def create_msg(context, subject, email, txt_mail_template, html_mail_template):
    """
    Creates an mail message from templates together with user and context data.
    """
    msg = EmailMultiAlternatives(
        subject,
        txt_mail_template.render(context),
        settings.DEFAULT_FROM_EMAIL,
        [email])
    msg.attach_alternative(html_mail_template.render(context), "text/html")
    return msg


def send_msg(msg):
    """
    Tries to send an email message and logs the result.
    """
    try:
        msg.send()
        logger.info("Info mail sent successfully.")
    except Exception:
        logger.exception("Exception occurred! Could not send mail.",
                         exc_info=True)
