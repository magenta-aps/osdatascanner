import structlog

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.contrib.auth.models import User
from django.template import loader

from .models.scannerjobs.scanner import Scanner, ScanStatus
from .models.usererrorlog import UserErrorLog

from os2datascanner.utils.template_utilities import (
        get_localised_template_names)

logger = structlog.get_logger("adminapp")


def send_mail_upon_completion(scanner: Scanner, scan_status: ScanStatus):
    """
    Send a mail to scannerjob responsible when a scannerjob has finished.
    """
    txt_mail_template = loader.select_template(
            get_localised_template_names(["mail/finished_scannerjob.txt"]))
    html_mail_template = loader.select_template(
            get_localised_template_names(["mail/finished_scannerjob.html"]))

    # Find suitable user to notify.
    username = scan_status.scan_tag.get("user")
    user = User.objects.filter(username=username).first() if username else None
    email = user.email if user else scanner.organization.contact_email

    context = create_context(scanner, scan_status, user)
    logger.info(f"Created context for info mail: {context}")

    msg = create_msg(context, user, email,
                     txt_mail_template, html_mail_template)

    send_msg(msg)


def create_context(scanner: Scanner, scan_status: ScanStatus, user: User):
    """
    Creates a context dict for the finished scannerjob ready for rendering.
    """
    user_logs = UserErrorLog.objects.filter(
        scan_status=scan_status).count()
    context = {
        "admin_login_url": settings.SITE_URL,
        "institution": settings.NOTIFICATION_INSTITUTION,
        "full_name": user.get_full_name() or user.username if user else "",
        "total_objects": scan_status.total_objects,
        "scanner_name": scanner.name,
        "object_size": scan_status.scanned_size,
        "completion_time": get_scanner_time(scan_status),
        "usererrorlogs": user_logs,
        "object_plural": scanner.as_subclass().object_name_plural,
    }

    return context


def get_scanner_time(scan_status: ScanStatus):
    """
    Calculates and formats the total runtime for the scannerjob.
    """
    total_time = scan_status.last_modified - scan_status.start_time

    hours = round(total_time.total_seconds() // 3600)
    minutes = round((total_time.total_seconds() % 3600) // 60)
    seconds = round((total_time.total_seconds() % 3600) % 60)

    return str(hours) + "t" + str(minutes) + "m" + str(seconds) + "s"


def create_msg(context, user, email, txt_mail_template, html_mail_template):
    """
    Creates an mail message from templates together with user and context data.
    """
    msg = EmailMultiAlternatives(
        "Dit OS2datascanner-scan er kørt færdigt.",
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
    except Exception as ex:
        logger.info(f"Could not send mail. Error: {ex}.")
