import datetime

import pytest
from io import StringIO
from django.conf import settings
from django.core.mail.message import EmailMultiAlternatives
from django.core.management import call_command
from django.template import loader
from os2datascanner.projects.report.reportapp.management.commands.send_notifications import \
    Command
from os2datascanner.projects.report.reportapp.models.documentreport import DocumentReport
from os2datascanner.utils.system_utilities import time_now


from os2datascanner.projects.report.tests.test_utilities import create_reports_for


@pytest.fixture
def send_notifications_command():
    command = Command()
    command.txt_mail_template = loader.get_template("mail/overview.txt")
    command.html_mail_template = loader.get_template("mail/overview.html")
    command.shared_context = {
        "image_name": None,
        "report_login_url": settings.SITE_URL,
        "institution": settings.NOTIFICATION_INSTITUTION
    }
    command.debug_message = {}
    command.debug_message["estimated_amount_of_users"] = 0
    command.debug_message["successful_amount_of_users"] = 0
    command.debug_message["unsuccessful_users"] = []
    command.debug_message["successful_users"] = []
    return command


@pytest.mark.django_db
class TestEmailNotification:

    def call_command(self, *args, **kwargs):
        out = StringIO()
        call_command(
            "send_notifications",
            *args,
            stdout=StringIO(),
            stderr=StringIO(),
            **kwargs,
        )
        return out.getvalue()

    def test_handle_(self):
        # test that it runs
        self.call_command('--all-results', '--dry-run')
        assert True

    def test_create_msg_without_image(self, send_notifications_command, egon_account):
        """ Asserts that a created email has the same properties,
             that we expect it to.
        """
        msg = send_notifications_command.create_email_message(
            None,
            None,
            send_notifications_command.shared_context,
            egon_account.user)

        excpected_msg = EmailMultiAlternatives(
            subject="Der ligger uhåndterede resultater i OSdatascanner",
            body=loader.get_template("mail/overview.txt").render(
                send_notifications_command.shared_context),
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[egon_account.user.email],
            attachments=[],
        )

        assert msg.subject == excpected_msg.subject
        assert msg.body == excpected_msg.body
        assert msg.from_email == excpected_msg.from_email
        assert msg.to == excpected_msg.to
        assert msg.attachments == excpected_msg.attachments

    @pytest.mark.parametrize('remediator_num,personal_num', [
        (1, 0),
        (0, 1),
        (1, 1),
        (10, 0),
        (0, 10),
        (10, 10),
    ])
    def test_count_user_results_remediator(
            self,
            send_notifications_command,
            egon_account,
            remediator_num,
            personal_num,
            egon_email_alias,
            egon_remediator_alias):
        """ Asserts that the command counts the correct amount of matches
            for a remediator
        """

        create_reports_for(egon_email_alias, num=personal_num)
        create_reports_for(egon_remediator_alias, num=remediator_num)

        result_user1 = send_notifications_command.count_user_results(
            all_results=True, results=DocumentReport.objects.filter(
                number_of_matches__gte=1, resolution_status__isnull=True), user=egon_account.user)

        assert result_user1["user_alias_bound_results"] == personal_num
        assert result_user1["remediator_bound_results"] == remediator_num
        assert result_user1["total_result_count"] == personal_num + remediator_num

    def test_schedule_check(self, send_notifications_command, olsenbanden_organization):
        olsenbanden_organization.email_notification_schedule = "RRULE:FREQ=DAILY"
        # Set an arbitrary day that's at least before _now_, as we wouldn't be including the
        # start day.
        olsenbanden_organization.dtstart = datetime.date(2024, 1, 1)
        olsenbanden_organization.save()

        # Check that a daily schedule will return True.
        assert send_notifications_command.schedule_check(olsenbanden_organization)

        # Check that a not scheduled day will return False.
        if time_now().weekday() != 0:
            olsenbanden_organization.email_notification_schedule = \
                "RRULE: FREQ = WEEKLY; BYDAY = MO"
        else:
            olsenbanden_organization.email_notification_schedule = \
                "RRULE: FREQ = WEEKLY; BYDAY = TU"
        olsenbanden_organization.save()

        assert not send_notifications_command.schedule_check(olsenbanden_organization)

        # Check that no schedule means we return false.
        olsenbanden_organization.email_notification_schedule = None
        olsenbanden_organization.save()
        assert not send_notifications_command.schedule_check(olsenbanden_organization)

    def test_schedule_check_weekly(self, olsenbanden_organization):

        # Arrange
        olsenbanden_organization.email_notification_schedule = \
            "RRULE:FREQ=WEEKLY;INTERVAL=2;BYDAY=MO"

        # This week's monday
        today = datetime.date.today()
        monday = today - datetime.timedelta(days=today.weekday())

        olsenbanden_organization.dtstart = monday
        olsenbanden_organization.save()

        monday_plus_1_week = monday + datetime.timedelta(weeks=1)
        monday_plus_2_weeks = monday + datetime.timedelta(weeks=2)

        # Act / Assert
        assert not olsenbanden_organization.get_next_email_schedule_date == monday_plus_1_week
        assert olsenbanden_organization.get_next_email_schedule_date == monday_plus_2_weeks
