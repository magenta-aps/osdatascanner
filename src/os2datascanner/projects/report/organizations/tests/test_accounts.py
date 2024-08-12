import datetime
import pytest

from django.utils import timezone
from django.contrib.auth import get_user_model

from ..models.account import StatusChoices, Account
from ...reportapp.models.documentreport import DocumentReport
from .utilities import make_matched_document_reports_for


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

    @pytest.mark.parametrize('all_matches,false_positives,rate', [
        (0, 0, 0),
        (10, 0, 0),
        (10, 3, 0.3),
        (10, 10, 1.0)
    ])
    def test_account_false_positive_rate(
            self,
            egon_email_alias,
            egon_account,
            olsenbanden_organization,
            all_matches,
            false_positives,
            rate):

        make_matched_document_reports_for(egon_email_alias, handled=all_matches, amount=all_matches)
        for report in DocumentReport.objects.filter(
                alias_relation=egon_email_alias)[:false_positives]:
            report.resolution_status = DocumentReport.ResolutionChoices.FALSE_POSITIVE
            report.save()

        assert egon_account.false_positive_rate == rate

    @pytest.mark.parametrize('egon_matches,benny_matches,egon_fp,benny_fp,alarm', [
        (0, 0, 0, 0, False),
        (10, 0, 10, 0, False),
        (10, 10, 0, 0, False),
        (10, 10, 5, 1, False),
        (10, 20, 10, 1, True)
    ])
    def test_account_false_positive_alarm(
            self,
            egon_email_alias,
            benny_email_alias,
            olsenbanden_organization,
            egon_account,
            benny_matches,
            egon_matches,
            benny_fp,
            egon_fp,
            alarm):

        make_matched_document_reports_for(
            egon_email_alias,
            handled=egon_matches,
            amount=egon_matches)
        make_matched_document_reports_for(
            benny_email_alias,
            handled=benny_matches,
            amount=benny_matches)

        for report in DocumentReport.objects.filter(alias_relation=benny_email_alias)[:benny_fp]:
            report.resolution_status = DocumentReport.ResolutionChoices.FALSE_POSITIVE
            report.save()

        for report in DocumentReport.objects.filter(alias_relation=egon_email_alias)[:egon_fp]:
            report.resolution_status = DocumentReport.ResolutionChoices.FALSE_POSITIVE
            report.save()

        assert egon_account.false_positive_alarm() == alarm


@pytest.mark.django_db
class TestUserAccountConnection:
    """Creating or interacting with an account should also create or alter a User."""

    def test_create_account_and_user(self, olsenbanden_organization):
        account = Account.objects.create(
            username="manden_med_planen",
            first_name="Egon",
            last_name="Olsen",
            is_superuser=True,
            organization=olsenbanden_organization
        )

        user = account.user

        assert user.username == account.username
        assert user.first_name == account.first_name
        assert user.last_name == account.last_name
        assert user.is_superuser == account.is_superuser

    def test_create_empty_account_and_user(self, olsenbanden_organization):
        account = Account.objects.create(
            username="username_mc_username",
            organization=olsenbanden_organization
        )

        user = account.user

        assert user.first_name == ""
        assert user.last_name == ""
        assert user.is_superuser is False

    # @pytest.mark.parametrize('field,value', [
    #     ('first_name', 'Jan'),
    #     ('last_name', 'Egeland'),
    #     ('username', 'super_muscle_pumping_crying_god'),
    #     ('is_superuser', True)
    # ])
    # def test_alter_account_and_user(self, egon_account, field, value):
    #     # This does not actually happen -- should it?
    #     setattr(egon_account, field, value)
    #     egon_account.save()

    #     user = egon_account.user
    #     assert getattr(user, field) == value

    def test_delete_user_with_account(self, egon_account):
        username = egon_account.username

        egon_account.delete()

        assert not get_user_model().objects.filter(username=username).exists()

    def test_bulk_create_account_and_user(self, olsenbanden_organization):
        accounts = Account.objects.bulk_create([
            Account(
                username='manden_med_planen',
                first_name='Egon',
                last_name='Olsen',
                is_superuser=True,
                organization=olsenbanden_organization
            )
        ])

        account = accounts[0]

        user = account.user

        assert user.username == account.username
        assert user.first_name == account.first_name
        assert user.last_name == account.last_name
        assert user.is_superuser == account.is_superuser

    def test_bulk_create_empty_account_and_user(self, olsenbanden_organization):
        accounts = Account.objects.bulk_create([
            Account(
                username='username_mc_username',
                organization=olsenbanden_organization
            )
        ])

        account = accounts[0]

        user = account.user

        assert user.first_name == ""
        assert user.last_name == ""
        assert user.is_superuser is False

    @pytest.mark.parametrize('field,value', [
        ('first_name', 'Jan'),
        ('last_name', 'Egeland'),
        ('username', 'super_muscle_pumping_crying_god'),
        ('is_superuser', True)
    ])
    def test_bulk_update_account_and_user(self, egon_account, field, value):
        setattr(egon_account, field, value)

        Account.objects.bulk_update([egon_account], fields=[field])

        user = egon_account.user
        assert getattr(user, field) == value

    def test_bulk_update_empty_account_and_user(self, olsenbanden_organization):
        account = Account.objects.create(
            username="username_mc_username",
            organization=olsenbanden_organization
        )

        account.username = "new_username"

        Account.objects.bulk_update([account], fields=['username'])

        user = account.user

        assert user.first_name == ""
        assert user.last_name == ""
        assert user.is_superuser is False
