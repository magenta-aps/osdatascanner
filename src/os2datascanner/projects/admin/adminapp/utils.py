# The contents of this file are subject to the Mozilla Public License
# Version 2.0 (the "License"); you may not use this file except in
# compliance with the License. You may obtain a copy of the License at
#    http://www.mozilla.org/MPL/
#
# Software distributed under the License is distributed on an "AS IS"basis,
# WITHOUT WARRANTY OF ANY KIND, either express or implied. See the License
# for the specific language governing rights and limitations under the
# License.
#
# OS2datascanner is developed by Magenta in collaboration with the OS2 public
# sector open source network <https://os2.eu/>.
#
"""Utility methods for the Admin application."""

from typing import NamedTuple

from django.utils import timezone

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
