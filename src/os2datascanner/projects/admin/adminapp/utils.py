# Part of the OSdatascanner system, copyright © 2014-2026 Magenta ApS.
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, you can
# obtain one at http://mozilla.org/MPL/2.0/.

"""Utility methods for the Admin application."""

from typing import NamedTuple

from django.utils import timezone
from django.conf import settings

from ..organizations.publish import publish_events
from ....utils.system_utilities import time_now


def upload_path_webscan_sitemap(instance, filename):
    return "organisation/%s" % instance.organization.slug + "/sitemaps/%s" % filename


def upload_path_gmail_service_account(instance, filename):
    return "organisation/%s" % instance.organization.slug + "/gmail/serviceaccount/%s" % filename


def upload_path_gmail_users(instance, filename):
    return "organisation/%s" % instance.organization.slug + "/gmail/users/%s" % filename


def upload_path_exchange_users(instance, filename):
    return "organisation/%s" % instance.organization.slug + "/mailscan/users/%s" % filename


def upload_path_gdrive_service_account(instance, filename):
    return ("organisation/%s" % instance.organization.slug
            + "/googledrive/serviceaccount/%s" % filename)


def upload_path_gdrive_users(instance, filename):
    return "organisation/%s" % instance.organization.slug + "/googledrive/users/%s" % filename


class CleanMessage(NamedTuple):
    """A CleanMessage contains a command from the admin module to the report
    module to 'clean' some part of the system, often DocumentReports."""
    time: timezone.datetime = None
    publisher: str = None
    event_type = "template_clean_message"
    scanners_accounts_dict: dict = None
    scanners: list = None

    def to_json_object(self):
        return {
            "type": self.event_type,
            "time": timezone.datetime.strftime(self.time, "%m/%d/%Y, %H:%M:%S"),
            "publisher": self.publisher,
            "scanners_accounts_dict": self.scanners_accounts_dict,
            "scanners": self.scanners
        }

    @classmethod
    def from_json_object(cls, obj):
        msg = cls()
        for attr, val in obj.items():
            setattr(msg, attr, val)
        return msg


class CleanAccountMessage(CleanMessage):
    """Contains a command from the admin module to the report module to delete
    reports related to sets of scanner jobs and accounts."""

    event_type = "clean_document_reports"

    @staticmethod
    def make_account_dict(accounts_) -> dict:
        # Capture accounts_ as a list to allow any Iterable[Account] argument
        # (a QuerySet, a generator, whatever)
        accounts = list(accounts_)
        return {
            "uuids": [str(a.uuid) for a in accounts],
            "usernames": [a.username for a in accounts]
        }

    @staticmethod
    def send(scanners_accounts_dict: dict, publisher="unknown"):
        """Publish the CleanMessage to the events queue, to be picked up by the
        event_collector in the report module.

        Expected structure of scanners_accounts_dict:
        {
            <scanner_pk_1>: {
                uuids: [
                    <uuid_1>,
                    <uuid_2>
                ],
                usernames: [
                    <username_1>,
                    <username_2>
                ]
            },
            <scanner_pk_2>: {
                uuids: [
                    <uuid_1>,
                    <uuid_3>
                ],
                usernames: [
                    <username_1>,
                    <username_3>
                ]
            }
        }
        """
        message = CleanAccountMessage(
            scanners_accounts_dict=scanners_accounts_dict,
            time=time_now(),
            publisher=publisher)
        publish_events([message])


class CleanProblemMessage(CleanMessage):
    """Contains a command from the admin module to the report module to delete
    DocumentReports with no matches related to specific scanners."""

    event_type = "clean_problem_reports"

    def send(scanners: list, publisher="unknown"):
        """Publish the CleanMessage to the events queue, to be picked up by the
        event_collector in the report module."""
        message = CleanProblemMessage(
            scanners=scanners,
            time=time_now(),
            publisher=publisher)
        publish_events([message])


class CoverageMessage(NamedTuple):
    """Message for communicating the account coverage of scannerjobs in the report module to the
    admin module."""
    coverages: list[dict[str, str]]

    def to_json_object(self):
        return {
            "coverages": self.coverages
        }

    @staticmethod
    def from_json_object(obj):
        return CoverageMessage(
            coverages=obj["coverages"]
        )


def is_expiring_soon(exp_date, today):
    """Determine if the expiry date is soon or overdue."""
    if exp_date:
        days_until_expiry = (exp_date - today).days
        return exp_date <= today or days_until_expiry <= settings.EXPIRATION_WARNING_THRESHOLD
    return False
