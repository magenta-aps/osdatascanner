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
    """A CleanMessage conveys a command from the admin module to the report
    module, that DocumentReport objects related to the given account UUID and
    scanner pk are to be deleted."""
    time = None
    publisher: str = None
    accounts: list[tuple] = []
    scanner_pk: list[int] = []
    event_type = "clean_document_reports"

    def to_json_object(self):
        return {
            "account_uuid": self.account_uuid,
            "scanner_pk": self.scanner_pk,
            "type": self.event_type,
            "time": self.time,
            "publisher": self.publisher
        }

    @staticmethod
    def from_json_object(obj):
        return CleanMessage(
            account_uuid=obj.get("account_uuid"),
            scanner_pk=obj.get("scanner_pk"),
            event_type=obj.get("type"),
            time=obj.get("time"),
            publisher=obj.get("publisher"))
