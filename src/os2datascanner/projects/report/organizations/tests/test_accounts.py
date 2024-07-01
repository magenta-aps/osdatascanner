import datetime
import json
import pytest

from django.utils import timezone

from ..models.account import StatusChoices
from ...reportapp.models.documentreport import DocumentReport


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


def make_matched_document_reports_for(alias, handled=0, amount=10, created=timezone.now()):
    for i in range(amount):
        dr = DocumentReport.objects.create(raw_matches=raw_matches_json_matched)
        dr.created_timestamp = created
        if i < handled:
            dr.resolution_status = 0
        dr.save()
        dr.alias_relation.add(alias)


@pytest.mark.django_db
class TestAccount:

    def test_save_with_no_new_matches_and_some_handled(
            self, egon_email_alias, egon_remediator_alias, egon_account):
        """If a user has not recently had new matches, their status should be
        'OK'."""

        handled_matches = 6
        all_matches = 10

        # Make documentreport that are > 3 weeks old.
        make_matched_document_reports_for(
            egon_email_alias,
            handled=handled_matches,
            amount=all_matches,
            created=timezone.now() -
            datetime.timedelta(
                days=100))

        # Matches related to a remediator should be ignored:
        make_matched_document_reports_for(egon_remediator_alias, handled=5, amount=10)

        # This is the real test. This is where .match_count and .match_status are set.
        egon_account.save()

        assert egon_account.match_count == all_matches-handled_matches
        assert egon_account.match_status == StatusChoices.OK

    @pytest.mark.parametrize("handled_num,all_num,status", [
        (100, 100, StatusChoices.GOOD),
        (0, 0, StatusChoices.GOOD),
        (0, 100, StatusChoices.BAD),
        (25, 100, StatusChoices.BAD),
        (50, 100, StatusChoices.BAD),
        (75, 100, StatusChoices.OK),
        (99, 100, StatusChoices.OK),
    ])
    def test_save_with_some_new_matches_and_some_handled(
            self, egon_account, egon_email_alias, handled_num, all_num, status):
        """If a user has not handled at least 75% of their matches the past
        3 weeks, their status should be 'BAD', otherwise it should be 'OK'.
        If the user has no matches at all, their status should be 'GOOD'."""

        make_matched_document_reports_for(egon_email_alias, handled=handled_num, amount=all_num)

        egon_account.save()

        assert all_num-handled_num == egon_account.match_count
        assert egon_account.match_status == status

    def test_save_with_no_new_matches_and_no_handled(self, egon_account, egon_email_alias):
        """If a user has not handled any matches, their status should be 'BAD',
        even if none of their matches are new."""

        # Egon has not done anything
        handled = 0
        all_matches = 10
        make_matched_document_reports_for(
            egon_email_alias,
            handled=handled,
            amount=all_matches,
            created=timezone.now() -
            datetime.timedelta(
                days=100))

        egon_account.save()

        assert all_matches-handled == egon_account.match_count
        assert egon_account.match_status == StatusChoices.BAD

    @pytest.mark.parametrize('num_weeks', [
        (-3),
        (0),
        (10),
        (104),
        (None)
    ])
    def test_count_matches_by_week_format(self, num_weeks, egon_account):
        """The count_matches_by_week-method should return a list of dicts with
        the following structure:
        [
            {
                "weeknum": <int>,
                "matches": <int>,
                "new": <int>,
                "handled": <int>
            },
            { ... }
        ]
        """

        if num_weeks is None:
            weekly_matches = egon_account.count_matches_by_week()
        elif num_weeks < 1:
            with pytest.raises(ValueError):
                egon_account.count_matches_by_week(weeks=num_weeks)
            return
        else:
            weekly_matches = egon_account.count_matches_by_week(weeks=num_weeks)

        assert len(weekly_matches) == num_weeks or 52
        for key in ("weeknum", "matches", "new", "handled"):
            assert key in weekly_matches[0].keys()

    def test_account_count_matches_by_week_created_none(self, egon_email_alias, egon_account):
        """Test the Account.count_matches_by_week-method with a report without
        a created timestamp, to make sure the method does not break."""
        make_matched_document_reports_for(egon_email_alias, handled=0, amount=1, created=None)
        weekly_matches = egon_account.count_matches_by_week(weeks=1)

        assert weekly_matches[0]["matches"] == 1

    def test_account_count_matches_from_ten_to_one_to_zero(self, egon_email_alias, egon_account):
        all_matches = 10
        handled = 0
        make_matched_document_reports_for(egon_email_alias, handled=handled, amount=all_matches)

        # Refresh match count.
        egon_account._count_matches()
        # Assert
        assert egon_account.match_count == all_matches

        # Handle 9/10

        DocumentReport.objects.filter(alias_relation=egon_email_alias).update(resolution_status=0)
        dr = DocumentReport.objects.filter(alias_relation=egon_email_alias).first()
        dr.resolution_status = None
        dr.save()
        # Refresh match count
        egon_account._count_matches()
        # Assert
        assert egon_account.match_count == 1

        # Handle all matches
        DocumentReport.objects.filter(alias_relation=egon_email_alias).update(resolution_status=0)
        # Refresh match count
        egon_account._count_matches()
        # Assert
        assert egon_account.match_count == 0

    def test_account_withheld_matches_from_ten_to_one_to_zero(self, egon_email_alias, egon_account):
        all_matches = 10
        handled = 0
        make_matched_document_reports_for(egon_email_alias, handled=handled, amount=all_matches)

        # Mark Egon's matches as withheld
        DocumentReport.objects.filter(alias_relation=egon_email_alias).update(
            only_notify_superadmin=True)

        # Refresh count
        egon_account._count_matches()
        # Assert
        assert egon_account.withheld_matches == 10
        assert egon_account.match_count == 0

        # Distribute 9 of  Egon's matches
        DocumentReport.objects.filter(alias_relation=egon_email_alias).update(
            only_notify_superadmin=False)
        dr = DocumentReport.objects.filter(alias_relation=egon_email_alias).first()
        dr.only_notify_superadmin = True
        dr.save()

        # Refresh count
        egon_account._count_matches()
        # Assert
        assert egon_account.withheld_matches == 1
        assert egon_account.match_count == 9

        # Distribute last one
        DocumentReport.objects.filter(alias_relation=egon_email_alias,
                                      only_notify_superadmin=True).update(
            only_notify_superadmin=False)
        # Refresh count
        egon_account._count_matches()
        # Assert, nothing should be withheld
        assert egon_account.withheld_matches == 0
        assert egon_account.match_count == 10
