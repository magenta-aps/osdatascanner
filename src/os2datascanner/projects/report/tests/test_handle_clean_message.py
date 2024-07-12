import pytest

from os2datascanner.projects.report.tests.test_utilities import create_reports_for

from ..reportapp.management.commands.event_collector import (
    handle_clean_account_message, handle_clean_problem_message)
from ..reportapp.models.documentreport import DocumentReport


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
