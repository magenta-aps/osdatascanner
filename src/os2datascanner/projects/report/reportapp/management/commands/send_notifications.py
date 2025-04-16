#!/usr/bin/env python
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
# OS2datascanner was developed by Magenta in collaboration with OS2 the
# Danish community of open source municipalities (https://os2.eu/).
#
# The code is currently governed by OS2 the Danish community of open
# source municipalities ( https://os2.eu/ )
from datetime import timedelta
from os.path import basename
from email.mime.image import MIMEImage

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.template import loader

from os2datascanner.utils.template_utilities import get_localised_template_names
from os2datascanner.utils.system_utilities import time_now

from ....organizations.models.account import Account
from ....organizations.models import Organization


class Command(BaseCommand):
    """
    Command used to send users an email notifications with information in regard to their
    delegated results. Ran in production by report/crontab.
    Can be run for debug or testing purposes by using and combining available flags.
    """
    help = __doc__

    def add_arguments(self, parser):
        parser.add_argument(
            "-a", "--all-results",
            action="store_true",
            help="Include results under 30 days in count."
        )
        parser.add_argument(
            "-cu", "--context-for-user",
            help="Print context for User pk to stdout",
            type=int,
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Summarise the emails that would be sent without sending them"
        )
        parser.add_argument(
            "-f", "--force",
            default=False,
            action="store_true",
            help="Send emails now, regardless of scheduling"
        )
        parser.add_argument(
            "--header-banner",
            default=True,
            action="store_true",
            help="Embed the specified image at the top of the email"
        )
        parser.add_argument(
            "-nu", "--notify-user",
            help="Sends email to User with provided pk if scheduled or ran with -f flag.",
            type=int,
        )

    def handle(self, *args, all_results, context_for_user,  # noqa CCR001
               dry_run, force, header_banner, notify_user, **options):

        for org in Organization.objects.all():
            # Evaluating if scheduled for today or ran with --f option.
            scheduled_today = self.schedule_check(org) if not force else force

            if scheduled_today:
                self.stdout.write(f"Performing email send-out for {org.name}")
                self.txt_mail_template = loader.select_template(
                    get_localised_template_names(["mail/overview.txt"]))
                self.html_mail_template = loader.select_template(
                    get_localised_template_names(["mail/overview.html"]))
                # Debug messages
                self.debug_message = {}
                self.debug_message["estimated_amount_of_users"] = 0
                self.debug_message["successful_amount_of_users"] = 0
                self.debug_message["unsuccessful_users"] = []
                self.debug_message["successful_users"] = []

                image_name = None
                image_content = None
                if header_banner and org.email_header_banner:
                    path = org.email_header_banner.path
                    with open(path, "rb") as fp:
                        image_content = fp.read()
                    image_name = basename(path)

                self.shared_context = {
                    "image_name": image_name,
                    "report_login_url": settings.SITE_URL,
                    "institution": settings.NOTIFICATION_INSTITUTION
                }

                if context_for_user or notify_user:
                    # Ensure provided user exists
                    try:
                        user = User.objects.get(pk=context_for_user or notify_user)
                        if results_context := self.count_user_results(all_results, user, org):
                            if context_for_user:
                                self.stdout.write(
                                    msg=f"Printing context for user: \n {results_context}",
                                    style_func=self.style.SUCCESS)
                            elif notify_user:
                                self.stdout.write(msg=f"Notifying user...\n"
                                                  f" Username: {user.username}\n"
                                                  f" PK: {notify_user} \n"
                                                  f" dry_run: {dry_run}",
                                                  style_func=self.style.SUCCESS)
                                email_message = self.create_email_message(image_name, image_content,
                                                                          results_context, user)
                                self.send_to_user(user, email_message, dry_run)

                    except User.DoesNotExist:
                        self.stdout.write(msg=f"User with pk {context_for_user} does not exist!",
                                          style_func=self.style.ERROR)

                # The "normal" behaviour. I.e. what happens when send-out occurs.
                else:
                    for user in User.objects.filter(account__organization=org):
                        if results_context := self.count_user_results(all_results, user, org):
                            email_message = self.create_email_message(image_name, image_content,
                                                                      results_context, user)
                            self.send_to_user(user, email_message, dry_run)

                    _ = self.debug_message
                    if not _["unsuccessful_users"] and _["successful_amount_of_users"] != 0:
                        debug = self.style.SUCCESS(
                            f'successfully sent {_["successful_amount_of_users"]} '
                            f'Email to following users'
                            f': {_["successful_users"]}')
                    else:
                        debug = self.style.ERROR(
                            f'successfully sent to {_["successful_amount_of_users"]} '
                            f'out of {_["estimated_amount_of_users"]} \n'
                            f'successful users: {_["successful_users"]} \n'
                            f'unsuccessful users: {_["unsuccessful_users"]}'
                        )

                    self.stdout.write(debug)

    def schedule_check(self, org) -> bool:
        """
         Performs a check of given orgs email notification schedule.
         Returns True if mails are to be sent today.
         False if no schedule or not scheduled today.
        """
        if not org.email_notification_schedule:
            # Org doesn't have mail notifications scheduled/have disabled it.
            self.stdout.write(f"Organization {org.name} has no email schedule.",
                              style_func=self.style.WARNING)
            return False

        else:
            # Recurrence field datetime is naive, which means we can't use an aware
            # datetime object.

            scheduled_next_date = org.get_next_email_schedule_date

            # We can when we're only concerned with the date.
            today_date = time_now().date()

            if not scheduled_next_date == today_date:
                self.stdout.write(f"Not performing email send-out for {org.name}. "
                                  f"Next scheduled date is: {scheduled_next_date}",
                                  style_func=self.style.WARNING)
                return False

            elif scheduled_next_date == today_date:
                # Bingo, today we must send mails.
                return True

    def count_user_results(self, all_results, user, org):
        """
            Counts results for a user and populates context used in email templates.
            Returns populated context or an empty dict if no results.
        """

        context = self.shared_context.copy()
        context["full_name"] = user.get_full_name() or user.username

        user_results = user.account.get_report(Account.ReportType.RAW)

        if org.retention_policy and not all_results:
            # If all_results is not provided, and the organization has a retention policy, do not
            # include results newer than the number of days specified by the policy.
            # Results of exactly the age of the retention policy are always included.
            time_threshold = time_now() - timedelta(days=org.retention_days)
            user_results = user_results.filter(
                datasource_last_modified__lte=time_threshold)

        if not user_results.exists():
            self.stdout.write(f"Nothing for user (username : {user.username}, pk : {user.pk})",
                              style_func=self.style.WARNING)
            return {}

        self.debug_message['estimated_amount_of_users'] += 1

        # Let the user know how many of these results are targeted for them.
        user_alias_bound_results = context["user_alias_bound_results"] = (
                user.account.get_report(Account.ReportType.PERSONAL).count())

        # If the user falls under either "superadmin" or remediator,
        # let the user know how many of these results stem from that.
        superadmin_bound_results = 0
        if user.is_superuser:
            superadmin_bound_results = context["superadmin_bound_results"] = (
                    user.account.get_report(
                            Account.ReportType.WITHHELD_AND_SHARED).count())
        remediator_bound_results = context["remediator_bound_results"] = (
                user.account.get_report(Account.ReportType.REMEDIATOR).count())

        context["total_result_count"] = (
                user_alias_bound_results
                + superadmin_bound_results
                + remediator_bound_results)

        return context

    def create_email_message(self, image_name, image_content, context, user):
        """ Creates an email message ready to send to a user.
        If an image has been provided, it will be used at the top of the mail.
        """

        email = self.get_user_email(user)
        self.stdout.write(f"User email detected: {email}")

        msg = EmailMultiAlternatives(
            "Der ligger uhåndterede resultater i OSdatascanner",
            self.txt_mail_template.render(context),
            settings.DEFAULT_FROM_EMAIL,
            [email])
        msg.attach_alternative(self.html_mail_template.render(context), "text/html")

        if image_name and image_content:
            mime_image = MIMEImage(image_content)
            mime_image.add_header('Content-ID', f'<{image_name}>')
            msg.attach(mime_image)

        return msg

    def get_user_email(self, user):
        account = Account.objects.filter(
            username=user.username).first()

        return account.email if account.email else user.email

    def send_to_user(self, user, msg, dry_run=False):
        email = self.get_user_email(user)
        try:
            if not dry_run:
                msg.send()
            self.debug_message['successful_users'].append({str(user): email})
            self.debug_message['successful_amount_of_users'] += 1
        except Exception as ex:
            self.stdout.write(self.style.ERROR(
                f'Exception occurred while trying to send an email: '
                f'{ex} to user {user}'))
            self.debug_message['unsuccessful_users'].append({str(user): email})
