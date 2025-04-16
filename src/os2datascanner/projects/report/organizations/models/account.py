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
import os
import structlog
from enum import auto, Enum
from PIL import Image
from datetime import timedelta
from rest_framework import serializers
from rest_framework.fields import UUIDField
from django.conf import settings
from django.db import models
from django.db.models import Count, Q, Case, When, Value, F, IntegerField, FloatField
from django.db.models.signals import post_save
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.contrib.auth.models import User, Permission
from django.dispatch import receiver
from django.db.models.signals import post_delete, m2m_changed


from os2datascanner.core_organizational_structure.models import Account as Core_Account
from os2datascanner.core_organizational_structure.models import \
    AccountSerializer as Core_AccountSerializer
from os2datascanner.core_organizational_structure.models.organization import \
    StatisticsPageConfigChoices, OutlookCategorizeChoices
from os2datascanner.core_organizational_structure.models.aliases import AliasType
from os2datascanner.utils.system_utilities import time_now


from ..seralizer import BaseBulkSerializer, SelfRelatingField

logger = structlog.get_logger("report_organizations")


class StatusChoices(models.IntegerChoices):
    GOOD = 0, _("Completed")
    OK = 1, _("Accepted")
    BAD = 2, _("Not accepted")


class AccountQuerySet(models.QuerySet):
    def create_account_outlook_setting(self, categorize_email: bool = False):
        """ Queryset method that'll create AccountOutlookSetting
        objects for every Account in queryset, that currently has none.
        """
        from ..models.account_outlook_setting import AccountOutlookSetting
        # Create AccountOutlook setting objects for those currently without.
        accounts_with_no_outlook_settings = self.filter(outlook_settings__isnull=True)

        # But also handle those who have objects (they might not be populated)
        outl_settings = AccountOutlookSetting.objects.filter(account__in=self)
        outl_settings.populate_setting()
        #  Trigger categorization of existing results
        outl_settings.categorize_existing()

        return AccountOutlookSetting.objects.bulk_create(
            [AccountOutlookSetting(account=account, categorize_email=categorize_email)
             for
             account in accounts_with_no_outlook_settings],
            ignore_conflicts=False  # If this is true, we can't get the PK in the return value.
        )

    def with_unhandled_matches(self):
        """Annotates each account in the queryset with 'unhandled_matches', which contains the
        number of unhandled matches the user has. Doesn't count matches from remediator aliases,
        shared aliases, or withheld matches.
        This field should contain the same value as the 'match_count' property."""
        return self.annotate(unhandled_matches=Count(
                    "aliases__match_relation",
                    filter=(
                        ~Q(aliases___alias_type=AliasType.REMEDIATOR)
                        & Q(
                            aliases__shared=False,
                            aliases__match_relation__number_of_matches__gte=1,
                            aliases__match_relation__resolution_status__isnull=True,
                            aliases__match_relation__only_notify_superadmin=False
                        )
                    ),
                    distinct=True
                )
            )

    def with_withheld_matches(self):
        """Annotates each account in the queryset with 'withheld', which contains the
        number of withheld matches the user has. Doesn't count matches from remediator aliases or
        shared aliases.
        This field should contain the same value as the 'withheld_matches' property."""
        return self.annotate(withheld=Count(
                    "aliases__match_relation",
                    filter=(
                        ~Q(aliases___alias_type=AliasType.REMEDIATOR)
                        & Q(
                            aliases__shared=False,
                            aliases__match_relation__number_of_matches__gte=1,
                            aliases__match_relation__resolution_status__isnull=True,
                            aliases__match_relation__only_notify_superadmin=True
                        )
                    ),
                    distinct=True
                )
            )

    def with_old_matches(self, policy: int):
        """Annotates each account in the queryset with 'old', which contains the number
        of matches older than the specified number of days the user has. Doesn't count matches from
        remediator aliases, shared aliases or withheld matches.
        This field should contain the same value as the 'old_matches' property."""
        if not policy >= 0:
            raise ValueError("The retention policy value given to the 'with_old_matches'-method "
                             f"must be a positive integer. Received {policy}")
        number_of_days_policy = policy
        cutoff_date = time_now() - timedelta(days=number_of_days_policy)
        return self.annotate(old=Count(
                    "aliases__match_relation",
                    filter=(
                        ~Q(aliases___alias_type=AliasType.REMEDIATOR)
                        & Q(
                            aliases__shared=False,
                            aliases__match_relation__number_of_matches__gte=1,
                            aliases__match_relation__resolution_status__isnull=True,
                            aliases__match_relation__only_notify_superadmin=False,
                            aliases__match_relation__datasource_last_modified__lte=cutoff_date
                        )
                    ),
                    distinct=True
                )
            )

    def with_status(self):
        """Annotates each account in the queryset with 'handle_status', which contains
        - StatusChoices.GOOD if they have no unhandled matches
        - StatusChoices.BAD if they have no handled matches in the last 3 weeks
          OR if the ratio between handled matches and new matches for the last 3 weeks in below 75%
        - StatusChoices.OK otherwise.
        This field should contain the same value as the 'match_status' property."""
        next_monday = timezone.now() + timedelta(weeks=1) - timedelta(
                days=timezone.now().weekday(),
                hours=timezone.now().hour,
                minutes=timezone.now().minute,
                seconds=timezone.now().second)

        three_weeks_ago = next_monday - timedelta(weeks=3)

        valid_reports = (~Q(aliases___alias_type=AliasType.REMEDIATOR)
                         & Q(aliases__shared=False,
                             aliases__match_relation__number_of_matches__gte=1,
                             aliases__match_relation__only_notify_superadmin=False
                             )
                         )
        unhandled_filter = Q(aliases__match_relation__resolution_status__isnull=True)
        handled_filter = Q(
            aliases__match_relation__resolution_status__isnull=False,
            aliases__match_relation__resolution_time__gte=three_weeks_ago)
        new_filter = Q(aliases__match_relation__created_timestamp__gte=three_weeks_ago)

        qs = self.annotate(
            _unhandled_count=Count(
                'aliases__match_relation',
                filter=valid_reports & unhandled_filter,
                distinct=True),
            _handled_count=Count(
                'aliases__match_relation',
                filter=valid_reports & handled_filter,
                distinct=True),
            _new_count=Count(
                'aliases__match_relation',
                filter=valid_reports & new_filter,
                distinct=True),
            _handled_new_ratio=Case(
                When(
                    _new_count__gt=0,
                    then=(F('_handled_count') * 1.0 / F('_new_count'))
                ),
                default=0.0,
                output_field=FloatField()))

        return qs.annotate(handle_status=Case(
                    When(_unhandled_count=0, then=Value(StatusChoices.GOOD)),
                    When(_handled_count=0, then=Value(StatusChoices.BAD)),
                    When(_handled_new_ratio__lt=0.75, then=Value(StatusChoices.BAD)),
                    default=Value(StatusChoices.OK),
                    output_field=IntegerField(),
                )
            )


class AccountManager(models.Manager):
    """ Account and User models come as a pair. AccountManager takes on the responsibility
    of creating User objects when Accounts are created.
    Unique to the report module.
    """

    def get_queryset(self):
        return AccountQuerySet(self.model, using=self._db, hints=self._hints)

    # TODO: Out-phase User in favor of Account
    # This is because User and Account co-exist, but a User doesn't have any unique identifier
    # that makes sense from an Account..
    # This means that we risk creating multiple User objects, if users username attribute changes.
    # It's the best we can do for now, until we out-phase User objects entirely

    def create(self, **kwargs):
        user_obj, created = User.objects.update_or_create(
            username=kwargs.get("username"),
            defaults={
                "first_name": kwargs.get("first_name") or '',
                "last_name": kwargs.get("last_name") or '',
                "is_superuser": kwargs.get("is_superuser", False)
            })
        account = Account(**kwargs, user=user_obj)
        account.save()

        if (account.organization.outlook_categorize_email_permission ==
                OutlookCategorizeChoices.ORG_LEVEL):
            acc_qs = Account.objects.filter(pk=account.pk)
            # Bulk creation of AccountOutlookSetting will then take care of the rest.
            acc_qs.create_account_outlook_setting(categorize_email=True)

        return account

    # We must also delete the User object.
    def delete(self, *args, **kwargs):
        self.user.delete()
        return super().delete(*args, **kwargs)

    def bulk_create(self, objs, **kwargs):

        for account in objs:
            user_obj, created = User.objects.update_or_create(
                username=account.username,
                defaults={
                    "first_name": account.first_name or '',
                    "last_name": account.last_name or '',
                    "is_superuser": account.is_superuser
                })
            account.user = user_obj

        objects = super().bulk_create(objs, **kwargs)

        accounts = Account.objects.filter(
            pk__in=[obj.pk for obj in objects]
        ).filter(
            organization__outlook_categorize_email_permission=OutlookCategorizeChoices.ORG_LEVEL)

        accounts.create_account_outlook_setting(categorize_email=True)

        return objects

    def bulk_update(self, objs, fields, **kwargs):
        if any(field in ("username", "first_name", "last_name", "is_superuser")
               for field in fields):
            for account in objs:
                user: User = account.user
                user.username = account.username
                user.first_name = account.first_name or ''
                user.last_name = account.last_name or ''
                user.is_superuser = account.is_superuser
                user.save()
        return super().bulk_update(objs, fields, **kwargs)


def weekly_match(**timestamps):
    """
    Returns a dict representing a summary
    of weekly matchs for a given week.
    """
    return {
        "matches": 0,
        "new": 0,
        "handled": 0,
        } | timestamps


class Account(Core_Account):
    """ Core logic lives in the core_organizational_structure app.
    Additional logic can be implemented here """

    serializer_class = None
    # Sets objects manager for Account
    objects = AccountManager()

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='account',
        verbose_name=_('User'),
        null=True,
        blank=True)
    last_handle = models.DateTimeField(
        verbose_name=_('Last handle'),
        null=True,
        blank=True)
    _image = models.ImageField(
        upload_to="media/images",
        default=None,
        null=True,
        blank=True,
        verbose_name=_('image'))
    contact_person = models.BooleanField(_("Contact person"), default=False)

    def update_last_handle(self):
        self.last_handle = time_now()
        self.save()

    @property
    def time_since_last_handle(self):
        """Return time since last handled, if the user has handled something.
        If not, return 3 days to trigger a warning to the user."""
        return (time_now() - self.last_handle).total_seconds() if self.last_handle else 60*60*24*3

    @property
    def image(self):
        return os.path.join(settings.MEDIA_ROOT, self._image.url) if self._image else None

    @property
    def status(self):
        return StatusChoices(self.match_status).label

    class ReportType(Enum):
        RAW = auto()
        """Select matches connected through any Alias."""

        PERSONAL = auto()
        """Select matches connected through any Alias that isn't shared and
        that isn't a remediator role."""

        PERSONAL_AND_SHARED = auto()
        """Select matches connected through any Alias that isn't a remediator
        role."""

        REMEDIATOR = auto()
        """Select matches connected through a remediator role Alias."""

        WITHHELD = auto()
        """Select matches held back for administrator review, connected through
        any Alias that isn't shared and that isn't a remediator role."""

        WITHHELD_AND_SHARED = auto()
        """Select matches held back for administrator review, connected through
        any Alias that isn't a remediator role."""

    def get_report(self, type_: ReportType, archived: bool = False):
        """Computes one of the standard report types for this Account. If you
        need to retrieve a subset of DocumentReports connected to a person,
        this method is almost invariably what you want."""
        from os2datascanner.projects.report.reportapp.models.documentreport \
            import DocumentReport

        select_withheld = type_ in (
                Account.ReportType.WITHHELD,
                Account.ReportType.WITHHELD_AND_SHARED,)

        qs = DocumentReport.objects.filter(
                organization=self.organization,
                number_of_matches__gte=1,
                resolution_status__isnull=not archived,
                only_notify_superadmin=select_withheld)

        rt = Account.ReportType  # Just to make the cases a bit tidier
        match type_:
            case rt.RAW:
                aliases = self.aliases.all()
            case rt.PERSONAL | rt.WITHHELD:
                # qs.exclude(cond_A, cond_B) excludes only those elements of qs
                # for which /both/ cond_A and cond_B are true, but we want to
                # exclude both independently here
                aliases = self.aliases.exclude(
                        _alias_type=AliasType.REMEDIATOR).exclude(shared=True)
            case rt.PERSONAL_AND_SHARED | rt.WITHHELD_AND_SHARED:
                aliases = self.aliases.exclude(
                        _alias_type=AliasType.REMEDIATOR)
            case rt.REMEDIATOR:
                aliases = self.aliases.filter(_alias_type=AliasType.REMEDIATOR)
            case _:
                raise TypeError(type_)

        return qs.filter(alias_relation__in=aliases).order_by(
                "sort_key", "pk").distinct()

    @property
    def match_count(self) -> int:
        """Counts the number of unhandled matches associated with the account."""
        return self.get_report(Account.ReportType.PERSONAL).count()

    @property
    def withheld_matches(self) -> int:
        return self.get_report(Account.ReportType.WITHHELD).count()

    @property
    def old_matches(self) -> int:
        if not self.organization.retention_policy:
            raise ValueError(f"Old matches requested from account {self}, but their organization "
                             f"{self.organization} does not have a retention policy!")
        number_of_days_policy = self.organization.retention_days
        cutoff_date = time_now() - timedelta(days=number_of_days_policy)
        reports = self.get_report(Account.ReportType.PERSONAL)
        reports = reports.filter(
            datasource_last_modified__lte=cutoff_date)
        return reports.count()

    @property
    def handled_matches(self) -> int:
        return self.get_report(Account.ReportType.PERSONAL, True).count()

    @property
    def match_status(self) -> StatusChoices:
        matches_by_week = self.count_matches_by_week(weeks=3, exclude_shared=True)

        total_new = 0
        total_handled = 0
        for week_obj in matches_by_week:
            total_new += week_obj["new"]
            total_handled += week_obj["handled"]

        if matches_by_week[0]["matches"] == 0:
            return StatusChoices.GOOD
        elif total_handled == 0 or (total_new != 0 and total_handled/total_new < 0.75):
            return StatusChoices.BAD
        else:
            return StatusChoices.OK

    @property
    def false_positive_rate(self) -> float:
        from os2datascanner.projects.report.reportapp.models.documentreport import DocumentReport
        all_matches = DocumentReport.objects.filter(
            alias_relation__account=self, number_of_matches__gte=1, resolution_status__isnull=False)
        fp_matches = all_matches.filter(
            resolution_status=DocumentReport.ResolutionChoices.FALSE_POSITIVE)

        return fp_matches.count() / all_matches.count() if all_matches.count() > 0 else 0

    @property
    def false_positive_percentage(self) -> float:
        return round(self.false_positive_rate * 100, 2)

    def false_positive_alarm(self) -> bool:
        org_fp_rate = self.organization.false_positive_rate
        acc_fp_rate = self.false_positive_rate

        # If the account's false positive rate is more than twice the
        # organization's false positive rate, raise the alarm!
        return acc_fp_rate > 2*org_fp_rate

    def count_matches_by_week(self, weeks: int = 52, exclude_shared=False):  # noqa: CCR001
        """
        This method counts the number of (unhandled) matches, the number of
        new matches and the number of handled matches on a weekly basis.

        Keyword arguments:
          weeks -- the number of weeks to count matches for.
        """
        if weeks < 1:
            raise ValueError("The number of weeks must be at least 1.")

        # This is placed here to avoid circular import
        from os2datascanner.projects.report.reportapp.models.documentreport import DocumentReport

        aliases = self.aliases.exclude(_alias_type=AliasType.REMEDIATOR)
        if exclude_shared:
            aliases = aliases.exclude(shared=True)

        all_matches = DocumentReport.objects.filter(
            number_of_matches__gte=1,
            alias_relation__in=aliases,
            only_notify_superadmin=False,
        ).values(
            "created_timestamp",
            "resolution_time",
            "resolution_status",
        )

        next_monday = timezone.now() + timedelta(weeks=1) - timedelta(
                days=timezone.now().weekday(),
                hours=timezone.now().hour,
                minutes=timezone.now().minute,
                seconds=timezone.now().second)

        def get_week(weeks: int):
            return next_monday - timedelta(weeks=weeks)

        matches_by_week = [
            weekly_match(begin_monday=get_week(i+1),
                         end_monday=get_week(i),
                         weeknum=get_week(i+1).isocalendar().week)
            for i in range(weeks)
        ]

        def is_this_week(week: dict, report: dict):
            """
            Checks of a report is created before the end of the week.
            """
            ctime = report.get("created_timestamp", None)
            return ctime and ctime < week["end_monday"]

        def is_unhandled(week: dict, report: dict):
            """
            Checks if a report is unhandled.

            A report is unhandled if either the status is null
            or the resolution time is either not set or in the future.
            """
            rtime = report.get("resolution_time", None)
            status = report.get("resolution_status", None)
            return status is None or not rtime or rtime > week["end_monday"]

        def is_handled(week: dict, report: dict):
            """
            Checks if a report is handled.

            A report is handled if the status is set and the resolution
            time is within this week.
            """
            rtime = report.get("resolution_time", None)
            status = report.get("resolution_status", None)
            return status is not None and week["begin_monday"] <= rtime < week["end_monday"]

        def is_new(week: dict, report: dict):
            """
            Check if a report is new.

            A report is new if the created timestamp is within
            this week.
            """
            ctime = report.get("created_timestamp", None)
            return ctime and week["begin_monday"] <= ctime < week["end_monday"]

        for week in matches_by_week:
            for report in all_matches:
                # set temporary timestamps if missing.
                if not report.get("created_timestamp"):
                    logger.warning(
                        "Encountered a DocumentReport object without a created_timestamp!")
                    report["created_timestamp"] = timezone.make_aware(timezone.datetime(1970, 1, 1))

                # Skip reports that are not in this week
                if not is_this_week(week, report):
                    continue

                if is_new(week, report):
                    week["new"] += 1

                if is_unhandled(week, report):
                    week["matches"] += 1
                elif is_handled(week, report):
                    week["handled"] += 1

        return matches_by_week

    def managed_by(self, account):
        units = self.units.all() & account.get_managed_units()
        return units.exists()

    @property
    def leadertab_access(self) -> bool:
        if (self.organization.leadertab_access == StatisticsPageConfigChoices.MANAGERS
                and (self.is_manager or self.user.is_superuser)):
            return True
        elif (self.organization.leadertab_access == StatisticsPageConfigChoices.SUPERUSERS
                and self.user.is_superuser):
            return True
        else:
            return False

    @property
    def dpotab_access(self) -> bool:
        if (self.organization.dpotab_access == StatisticsPageConfigChoices.DPOS
                and (self.is_dpo or self.user.is_superuser)):
            return True
        elif (self.organization.dpotab_access == StatisticsPageConfigChoices.SUPERUSERS
                and self.user.is_superuser):
            return True
        else:
            return False


@receiver(post_save, sender=Account)
def resize_image(sender, **kwargs):
    size = (300, 300)
    try:
        with Image.open(kwargs["instance"]._image.path) as image:
            image.thumbnail(size, Image.ANTIALIAS)
            image.save(kwargs["instance"]._image.path, optimize=True)
    except ValueError:
        logger.debug("image resize failed", exc_info=True)


def get_permissions_from_codenames(codenames: list[dict]) -> models.QuerySet[Permission]:
    """Converts permission objects from the serializer into a queryset of Permission objects."""
    codenames = [d["codename"] for d in codenames] if codenames else []
    permissions = Permission.objects.filter(content_type__model="syncedpermission",
                                            codename__in=codenames)
    return permissions


class AccountBulkSerializer(BaseBulkSerializer):
    """ Bulk create & update logic lives in BaseBulkSerializer """
    class Meta:
        model = Account

    def create(self, validated_data):
        permissions = [obj_attrs.pop("permissions") for obj_attrs in validated_data]
        accs = super().create(validated_data)
        for acc, perm in zip(accs, permissions):
            acc_perms = get_permissions_from_codenames(perm)
            acc.permissions.set(acc_perms)
        return accs

    def update(self, instances, validated_data):
        permissions = [obj_attrs.pop("permissions") for obj_attrs in validated_data]
        accs = super().update(instances, validated_data)
        for acc, perm in zip(accs, permissions):
            acc_perms = get_permissions_from_codenames(perm)
            acc.permissions.set(acc_perms)
        return accs


class AccountSerializer(Core_AccountSerializer):

    pk = serializers.UUIDField(read_only=False)
    from ..models.organization import Organization
    organization = serializers.PrimaryKeyRelatedField(
        queryset=Organization.objects.all(),
        required=True,
        allow_null=False,
        pk_field=UUIDField(format='hex_verbose')
    )
    # Note that this is a PrimaryKeyRelatedField in the admin module.
    # Since manager is a self-referencing foreign-key however, we can't use that here, as we
    # cannot guarantee the manager Account exists in the database when doing bulk creates.
    manager = SelfRelatingField(
        queryset=Account.objects.all(),
        many=False,
        required=False,
        allow_null=True,
    )

    class Meta(Core_AccountSerializer.Meta):
        model = Account
        list_serializer_class = AccountBulkSerializer


Account.serializer_class = AccountSerializer


@receiver(post_delete, sender=Account)
def post_delete_user(sender, instance, *args, **kwargs):
    if instance.user:
        instance.user.delete()


@receiver(m2m_changed, sender=Account.permissions.through)
def permissions_changed(sender, instance, *args, **kwargs):
    instance.user.user_permissions.set(instance.permissions.all())
