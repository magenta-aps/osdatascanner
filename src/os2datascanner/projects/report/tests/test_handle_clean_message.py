import json
import pytest

from ..reportapp.management.commands.event_collector import (
    handle_clean_account_message, handle_clean_problem_message)
from ..reportapp.utils import create_alias_and_match_relations
from ..reportapp.models.documentreport import DocumentReport

# This is a real raw_matches field from test data. This could probably be done
# in a better way.
raw_matches_json_matched = json.loads('''
{
  "handle": {
    "path": "Flere sider.html",
    "type": "lo-object",
    "source": {
      "type": "lo",
      "handle": {
        "path": "/Flere sider.docx",
        "type": "web",
        "source": {
          "url": "http://nginx",
          "type": "web",
          "exclude": [],
          "sitemap": null
        },
        "referrer": {
          "path": "/",
          "type": "web",
          "source": {
            "url": "http://nginx",
            "type": "web",
            "exclude": [],
            "sitemap": null
          },
          "last_modified": null
        },
        "last_modified": null
      }
    }
  },
  "origin": "os2ds_matches",
  "matched": true,
  "matches": [
    {
      "rule": {
        "name": "CPR regel",
        "type": "cpr",
        "blacklist": [
          "tullstatistik",
          "fakturanummer",
          "p-nummer",
          "p-nr",
          "fak-nr",
          "customer-no",
          "p.nr",
          "faknr",
          "customer no",
          "dhk:tx",
          "bilagsnummer",
          "test report no",
          "tullstatistisk",
          "ordrenummer",
          "pnr",
          "protocol no.",
          "order number"
        ],
        "whitelist": [
          "cpr"
        ],
        "modulus_11": true,
        "sensitivity": 1000,
        "ignore_irrelevant": true
      },
      "matches": [
        {
          "match": "1111XXXXXX",
          "offset": 1,
          "context": "XXXXXX-XXXX XXXXXX-XXXX XXXXXX-XXXX XXXXXX-XXXX",
          "probability": 1.0,
          "sensitivity": 1000,
          "context_offset": 1
        },
        {
          "match": "1111XXXXXX",
          "offset": 22,
          "context": "XXXXXX-XXXX XXXXXX-XXXX XXXXXX-XXXX XXXXXX-XXXX XXXXXX-XXXX",
          "probability": 1.0,
          "sensitivity": 1000,
          "context_offset": 22
        },
        {
          "match": "1111XXXXXX",
          "offset": 33,
          "context": "XXXXXX-XXXX XXXXXX-XXXX XXXXXX-XXXX XXXXXX-XXXX XXXXXX-XXXX",
          "probability": 1.0,
          "sensitivity": 1000,
          "context_offset": 33
        },
        {
          "match": "1111XXXXXX",
          "offset": 48,
          "context": "XXXXXX-XXXX XXXXXX-XXXX XXXXXX-XXXX XXXXXX-XXXX XXXXXX-XXXX",
          "probability": 1.0,
          "sensitivity": 1000,
          "context_offset": 48
        },
        {
          "match": "1111XXXXXX",
          "offset": 63,
          "context": "XXXXXX-XXXX XXXXXX-XXXX XXXXXX-XXXX XXXXXX-XXXX",
          "probability": 1.0,
          "sensitivity": 1000,
          "context_offset": 50
        }
      ]
    }
  ],
  "scan_spec": {
    "rule": {
      "name": "CPR regel",
      "type": "cpr",
      "blacklist": [
        "tullstatistik",
        "fakturanummer",
        "p-nummer",
        "p-nr",
        "fak-nr",
        "customer-no",
        "p.nr",
        "faknr",
        "customer no",
        "dhk:tx",
        "bilagsnummer",
        "test report no",
        "tullstatistisk",
        "ordrenummer",
        "pnr",
        "protocol no.",
        "order number"
      ],
      "whitelist": [
        "cpr"
      ],
      "modulus_11": true,
      "sensitivity": 1000,
      "ignore_irrelevant": true
    },
    "source": {
      "type": "lo",
      "handle": {
        "path": "/Flere sider.docx",
        "type": "web",
        "source": {
          "url": "http://nginx",
          "type": "web",
          "exclude": [],
          "sitemap": null
        },
        "referrer": {
          "path": "/",
          "type": "web",
          "source": {
            "url": "http://nginx",
            "type": "web",
            "exclude": [],
            "sitemap": null
          },
          "last_modified": null
        },
        "last_modified": null
      }
    },
    "progress": null,
    "scan_tag": {
      "time": "2023-01-05T11:32:26+01:00",
      "user": "dev",
      "scanner": {
        "pk": 2,
        "name": "Local nginx",
        "test": false
      },
      "destination": "pipeline_collector",
      "organisation": {
        "name": "OS2datascanner",
        "uuid": "0e18b3f2-89b6-4200-96cd-38021bbfa00f"
      }
    },
    "filter_rule": null,
    "configuration": {
      "skip_mime_types": [
        "image/*"
      ]
    }
  }
}
''')


def create_reports_for(alias, num=10, scanner_job_pk=1, matched=True):
    for i in range(num):
        DocumentReport.objects.create(
            name=f"Report-{i}{'-matched' if matched else ''}",
            owner=alias._value,
            scanner_job_pk=scanner_job_pk,
            path=(f"report-{i}-{scanner_job_pk}-{alias.account.username}"
                  f"-{'matched' if matched else 'unmatched'}"),
            raw_matches=raw_matches_json_matched if matched else None)

    create_alias_and_match_relations(alias)


@pytest.fixture
def egon_and_bøffen_reports_from_two_scannerjobs(egon_email_alias, bøffen_email_alias):
    create_reports_for(egon_email_alias, num=10, scanner_job_pk=1)
    create_reports_for(bøffen_email_alias, num=10, scanner_job_pk=1)
    create_reports_for(egon_email_alias, num=10, scanner_job_pk=2)
    create_reports_for(bøffen_email_alias, num=10, scanner_job_pk=2)


@pytest.fixture
def bøffen_matched_and_unmatched_reports_two_scannerjobs(bøffen_email_alias):
    create_reports_for(bøffen_email_alias, num=10, scanner_job_pk=1, matched=True)
    create_reports_for(bøffen_email_alias, num=10, scanner_job_pk=1, matched=False)
    create_reports_for(bøffen_email_alias, num=10, scanner_job_pk=2, matched=False)


@pytest.mark.django_db
class TestHandleCleanAccountMessage:

    def test_cleaning_document_reports_single_account_and_scanner(
            self,
            bøffen_account,
            egon_account,
            egon_and_bøffen_reports_from_two_scannerjobs):
        """Giving a CleanMessage to the event_message_received_raw-function
        should delete all DocumentReport-objects associated with the given
        account and scanner."""

        message = {
            "scanners_accounts_dict": {
              1: {
                "uuids": [bøffen_account.uuid],
                "usernames": [bøffen_account.username]
              }
            },
            "type": "clean_document_reports"}

        handle_clean_account_message(message)

        assert DocumentReport.objects.count() == 30
        assert DocumentReport.objects.filter(
            alias_relation__account=bøffen_account,
            scanner_job_pk=1
        ).count() == 0
        assert DocumentReport.objects.filter(
            alias_relation__account=bøffen_account,
        ).exclude(
            scanner_job_pk=1
        ).count() == 10
        assert DocumentReport.objects.filter(
            alias_relation__account=egon_account
        ).count() == 20

    def test_cleaning_document_reports_with_no_scanners(
            self,
            bøffen_account,
            egon_account,
            egon_and_bøffen_reports_from_two_scannerjobs):
        """Giving a CleanMessage to the event_message_received_raw-function
        without a scanner_job_pk should not delete any DocumentReport-objects."""
        message = {
            "scanners_accounts_dict": {},
            "type": "clean_document_reports"}

        handle_clean_account_message(message)

        assert DocumentReport.objects.count() == 40
        assert DocumentReport.objects.filter(
            alias_relation__account=bøffen_account
        ).count() == 20
        assert DocumentReport.objects.filter(
            alias_relation__account=egon_account
        ).count() == 20

    def test_cleaning_document_reports_multiple_accounts_single_scanner(
            self,
            bøffen_account,
            egon_account,
            egon_and_bøffen_reports_from_two_scannerjobs):
        """Giving a CleanMessage to the event_message_received_raw-function
        should delete all DocumentReport-objects associated with the given
        accounts and scanner."""
        message = {
            "scanners_accounts_dict": {
              1: {
                "uuids": [str(bøffen_account.uuid), str(egon_account.uuid)],
                "usernames": [bøffen_account.username, egon_account.username]
              }
            },
            "type": "clean_document_reports"}

        handle_clean_account_message(message)

        assert DocumentReport.objects.count() == 20
        assert DocumentReport.objects.filter(
            alias_relation__account=bøffen_account,
            scanner_job_pk=1
        ).count() == 0
        assert DocumentReport.objects.filter(
            alias_relation__account=bøffen_account,
        ).exclude(
            scanner_job_pk=1
        ).count() == 10
        assert DocumentReport.objects.filter(
            alias_relation__account=egon_account,
            scanner_job_pk=1
        ).count() == 0
        assert DocumentReport.objects.filter(
            alias_relation__account=egon_account,
        ).exclude(
            scanner_job_pk=1
        ).count() == 10

    def test_cleaning_document_reports_single_account_multiple_scanners(
            self,
            bøffen_account,
            egon_account,
            egon_and_bøffen_reports_from_two_scannerjobs):
        """Giving a CleanMessage to the event_message_received_raw-function
        should delete all DocumentReport-objects associated with the given
        account and scanners."""
        message = {
            "scanners_accounts_dict": {
              1: {
                "uuids": [str(bøffen_account.uuid)],
                "usernames": [bøffen_account.username]
              },
              2: {
                "uuids": [str(bøffen_account.uuid)],
                "usernames": [bøffen_account.username]
              }
            },
            "type": "clean_document_reports"}

        handle_clean_account_message(message)

        assert DocumentReport.objects.count() == 20
        assert DocumentReport.objects.filter(
            alias_relation__account=bøffen_account,
            scanner_job_pk__in=[1, 2]
        ).count() == 0
        assert DocumentReport.objects.filter(
            alias_relation__account=bøffen_account,
        ).exclude(
            scanner_job_pk__in=[1, 2]
        ).count() == 0
        assert DocumentReport.objects.filter(
            alias_relation__account=egon_account
        ).count() == 20

    def test_cleaning_document_reports_multiple_accounts_and_scanners(
            self,
            bøffen_account,
            egon_account,
            egon_and_bøffen_reports_from_two_scannerjobs):
        """Giving a CleanMessage to the event_message_received_raw-function
        should delete all DocumentReport-objects associated with the given
        accounts and scanners."""
        message = {
            "scanners_accounts_dict": {
              1: {
                "uuids": [str(bøffen_account.uuid), str(egon_account.uuid)],
                "usernames": [bøffen_account.username, egon_account.username]
              },
              2: {
                "uuids": [str(bøffen_account.uuid), str(egon_account.uuid)],
                "usernames": [bøffen_account.username, egon_account.username]
              }
            },
            "type": "clean_document_reports"}

        handle_clean_account_message(message)

        assert DocumentReport.objects.filter(
            alias_relation__account=bøffen_account,
            scanner_job_pk=1).count() == 0
        assert DocumentReport.objects.filter(
            alias_relation__account=bøffen_account,
            scanner_job_pk=2).count() == 0
        assert DocumentReport.objects.filter(
            alias_relation__account=egon_account,
            scanner_job_pk=1).count() == 0
        assert DocumentReport.objects.filter(
            alias_relation__account=egon_account,
            scanner_job_pk=2).count() == 0


@pytest.mark.django_db
class TestHandleCleanProblemMessage:

    def test_cleaning_problems_one_scanner(
            self,
            bøffen_matched_and_unmatched_reports_two_scannerjobs):
        """Cleaning problems for one scanner should not touch problems from
        other scanners."""
        message = {
            "scanners": [1],
            "type": "clean_problem_reports"
        }
        handle_clean_problem_message(message)

        # Make sure only the ten unmatched reports were deleted
        assert DocumentReport.objects.all().count() == 20
        assert DocumentReport.objects.filter(
            scanner_job_pk=1,
            number_of_matches=0
        ).count() == 0

        # Make sure reports from other scanner are untouched
        assert DocumentReport.objects.filter(
            scanner_job_pk=2
        ).count() == 10

    def test_cleaning_problems_for_two_scanners(
            self,
            bøffen_matched_and_unmatched_reports_two_scannerjobs):
        """Cleaning problems for multiple scanners should remove problems
        from both."""
        message = {
            "scanners": [1, 2],
            "type": "clean_problem_reports"
        }
        handle_clean_problem_message(message)

        # Make sure only problem reports were deleted
        assert DocumentReport.objects.all().count() == 10
        assert DocumentReport.objects.filter(
            scanner_job_pk=1,
            number_of_matches=0
        ).count() == 0
        assert DocumentReport.objects.filter(
            scanner_job_pk=2,
            number_of_matches=0
        ).count() == 0
