import requests
import structlog
from django.core.exceptions import PermissionDenied
from django.db import models
from django.conf import settings
from django.db.models import Q
from django.utils.translation import gettext_lazy as _

from os2datascanner.engine2.model.msgraph import MSGraphMailMessageHandle
from .account import Account
from os2datascanner.projects.report.reportapp.views.utilities.msgraph_utilities import (
    get_msgraph_mail_document_reports,
    get_handle_from_document_report)
from os2datascanner.core_organizational_structure.models.organization import (
    OutlookCategorizeChoices)

logger = structlog.get_logger("report_organizations")


class AccountOutlookSettingQuerySet(models.QuerySet):
    from os2datascanner.engine2.model.msgraph.utilities import MSGraphSource
    GraphCaller = MSGraphSource.GraphCaller

    # TODO: We should get tenant ID from a synchronized Grant.
    def _make_token(self):
        from os2datascanner.engine2.model.msgraph.utilities import make_token
        return make_token(
            settings.MSGRAPH_APP_ID,
            settings.MSGRAPH_TENANT_ID,
            settings.MSGRAPH_CLIENT_SECRET)

    def _initiate_graphcaller(self, session) -> GraphCaller | None:
        """ Returns a GraphCaller if queryset is populated, None if not."""
        # We want to create the GraphCaller before iterating for reuse purposes,
        # but we'll not want to create one, if we have an empty Queryset
        return self.GraphCaller(self._make_token, session) if self else None

    def populate_setting(self) -> str:  # noqa: CCR001 Too complex
        def _create_category(owner, category_name, category_colour):
            log = logger.bind(owner=owner,
                              category_name=category_name,
                              category_colour=category_colour)

            try:
                response = gc.create_outlook_category(
                    owner, category_name=category_name,
                    category_colour=category_colour
                )
                if response.ok:
                    log.info("Successfully created Outlook Category")
                    return response.json().get("id")

            except requests.HTTPError as ex:
                if ex.response.status_code == 409:  # Conflict / Already exists
                    try:
                        master_categories = gc.paginated_get(
                            f"users/{owner}/outlook/masterCategories")
                        for category in master_categories:
                            if category.get("displayName") == category_name:
                                log.info("Found existing category! Fetching ID..")
                                return category.get("id")
                    except requests.HTTPError as ex:
                        log.warning("Couldn't fetch existing category!", response=ex.response)

                else:
                    log.warning("Couldn't create category!", response=ex.response)
                    return None

        # Only objects that don't have either a match or fp category are relevant for inspection.
        qs = self.exclude(
            Q(outlook_categories__name=OutlookCategory.OutlookCategoryNames.MATCH) &
            Q(outlook_categories__name=OutlookCategory.OutlookCategoryNames.FALSE_POSITIVE))

        with requests.Session() as session:
            gc = self._initiate_graphcaller(session)
            created_category_count = 0

            for outl_setting in qs:
                # TODO: ENUM use should be refactored to support name change.
                if not outl_setting.match_category:
                    match_uuid = _create_category(outl_setting.account.email,
                                                  "OSdatascanner Match",
                                                  OutlookCategory.OutlookCategoryColour.DarkRed)
                    if match_uuid:
                        OutlookCategory.objects.create(
                            category_name="OSdatascanner Match",
                            category_colour=OutlookCategory.OutlookCategoryColour.DarkRed,
                            category_uuid=match_uuid,
                            name=OutlookCategory.OutlookCategoryNames.MATCH,
                            account_outlook_setting=outl_setting)
                        created_category_count += 1

                if not outl_setting.false_positive_category:
                    fp_uuid = _create_category(outl_setting.account.email,
                                               "OSdatascanner False Positive",
                                               OutlookCategory.OutlookCategoryColour.DarkGreen)
                    if fp_uuid:
                        OutlookCategory.objects.create(
                            category_name="OSdatascanner False Positive",
                            category_colour=OutlookCategory.OutlookCategoryColour.DarkGreen,
                            category_uuid=fp_uuid,
                            name=OutlookCategory.OutlookCategoryNames.FALSE_POSITIVE,
                            account_outlook_setting=outl_setting)
                        created_category_count += 1

                # TODO: Perhaps convert to bulk updates
                outl_setting.categorize_email = True
                outl_setting.save()
                logger.info(f"Saved {outl_setting}")

            return _(f"Created {created_category_count} categories!")

    def categorize_existing(self) -> str:  # noqa: CCR001 Too complex

        qs = self.select_related("account")
        with requests.Session() as session:
            gc = self._initiate_graphcaller(session)
            categorized_count = 0
            # TODO: does JSON-batching make sense here? (MSGraph API)
            for outl_setting in qs:
                doc_reps = []
                # TODO: this is weird.. having to encapsulate in try except to do a filter.
                try:
                    doc_reps = get_msgraph_mail_document_reports(outl_setting.account)
                except PermissionDenied:
                    logger.info(f"No msgraph-mail document reports for {outl_setting.account}")

                for doc_rep in doc_reps:
                    message_handle = get_handle_from_document_report(doc_rep,
                                                                     MSGraphMailMessageHandle)
                    msg_id = message_handle.relative_path if message_handle else None
                    try:
                        existing_categories_response = gc.get(
                            f"users/{outl_setting.account.email}/messages/{msg_id}?$select"
                            f"=categories").json()

                        email_categories = existing_categories_response.get("categories", [])

                        # Only append if it isn't already marked.
                        # TODO: refactor to not use ENUM
                        if not any(category.category_name in email_categories for category in
                                   outl_setting.outlook_categories.all()):
                            email_categories.append(outl_setting.match_category.category_name)

                        categorize_email_response = gc.categorize_mail(
                            outl_setting.account.email,
                            msg_id,
                            email_categories)

                        if categorize_email_response.ok:
                            categorized_count += 1
                            logger.info(
                                f"Successfully added category "
                                f"{outl_setting.match_category.category_name} to email for: "
                                f"{outl_setting.account.email}!")

                    except requests.HTTPError as ex:
                        # We don't want to raise anything here, as we're iterating emails.
                        # The most likely scenario is just that the mail doesn't exist anymore.
                        logger.warning(f"Couldn't categorize email! Got response: {ex.response}")

            return _(f"Successfully categorized {categorized_count} emails!")

    def update_colour(self, match_colour, fp_colour) -> str:
        with requests.Session() as session:
            gc = self._initiate_graphcaller(session)
            updated_category_count = 0
            for outl_setting in self:
                try:
                    if outl_setting.match_category.category_colour != match_colour:
                        match_resp = gc.update_category_colour(
                            outl_setting.account.email,
                            outl_setting.match_category.category_uuid,
                            match_colour)

                        if match_resp.ok:
                            logger.info(f"Updated Match colour to {match_colour}!")
                            updated_category_count += 1

                    if outl_setting.false_positive_category.category_colour != fp_colour:
                        fp_resp = gc.update_category_colour(
                            outl_setting.account.email,
                            outl_setting.false_positive_category.category_uuid,
                            fp_colour)

                        if fp_resp.ok:
                            logger.info(f"Updated False Positive colour to {fp_colour}!")
                            updated_category_count += 1

                except requests.HTTPError as ex:
                    logger.warning(f"Couldn't update colour! Got response: {ex.response}")

            # Update database
            OutlookCategory.objects.filter(
                name=OutlookCategory.OutlookCategoryNames.MATCH).update(
                category_colour=match_colour)
            OutlookCategory.objects.filter(
                name=OutlookCategory.OutlookCategoryNames.FALSE_POSITIVE).update(
                category_colour=fp_colour)
            return _(f"Updated {updated_category_count} categories!")

    def delete_categories(self) -> str:
        with requests.Session() as session:
            gc = self._initiate_graphcaller(session)
            # TODO: does JSON-batching make sense here? (MSGraph API)
            deleted_category_count = 0
            for outl_setting in self:
                try:
                    delete_match_category_response = gc.delete_category(
                        outl_setting.account.email,
                        outl_setting.match_category.category_uuid)
                    if delete_match_category_response.ok:
                        logger.info(f"Successfully deleted Match "
                                    f"Outlook Category for {outl_setting.account}! ")
                        deleted_category_count += 1

                    delete_fp_response = gc.delete_category(
                        outl_setting.account.email,
                        outl_setting.false_positive_category.category_uuid)
                    if delete_fp_response.ok:
                        logger.info(f"Successfully deleted False Positive "
                                    f"Outlook Category for {outl_setting.account}! ")
                        deleted_category_count += 1

                except requests.HTTPError as ex:
                    logger.warning(f"Couldn't delete category! Got response: {ex.response}")

            # Update database
            self.update(categorize_email=False)
            OutlookCategory.objects.filter(account_outlook_setting__in=self).delete()
            return _(f"Deleted {deleted_category_count} categories!")

    def bulk_create(self, objs, **kwargs):
        objects = super().bulk_create(objs, **kwargs)
        outl_settings = (AccountOutlookSetting.objects.filter(
            pk__in=[obj.pk for obj in objects]).filter(
            account__organization__outlook_categorize_email_permission=OutlookCategorizeChoices.ORG_LEVEL))  # noqa: E501, can't make line shorter.
        # Create categories
        outl_settings.populate_setting()
        #  Trigger categorization of existing results
        outl_settings.categorize_existing()

        return objects


class AccountOutlookSetting(models.Model):

    objects = AccountOutlookSettingQuerySet.as_manager()

    account = models.OneToOneField(Account,
                                   on_delete=models.CASCADE,
                                   related_name="outlook_settings")

    categorize_email = models.BooleanField(default=False,
                                           verbose_name=_("Categorize emails"))

    @property
    def match_category(self):
        try:
            return self.outlook_categories.get(name=OutlookCategory.OutlookCategoryNames.MATCH)
        except OutlookCategory.DoesNotExist:
            return None

    @property
    def false_positive_category(self):
        try:
            return self.outlook_categories.get(
                name=OutlookCategory.OutlookCategoryNames.FALSE_POSITIVE)
        except OutlookCategory.DoesNotExist:
            return None


class OutlookCategory(models.Model):
    class OutlookCategoryColour(models.TextChoices):
        # Available colour presets are defined here:
        # https://learn.microsoft.com/en-us/graph/api/resources/outlookcategory?view=graph-rest-1.0#properties
        Red = "Preset0", _("Red")
        Orange = "Preset1", _("Orange")
        Brown = "Preset2", _("Brown")
        Yellow = "Preset3", _("Yellow")
        Green = "Preset4", _("Green")
        Teal = "Preset5", _("Teal")
        Olive = "Preset6", _("Olive")
        Blue = "Preset7", _("Blue")
        Purple = "Preset8", _("Purple")
        Cranberry = "Preset9", _("Cranberry")
        Steel = "Preset10", _("Steel")
        DarkSteel = "Preset11", _("Dark Steel")
        Gray = "Preset12", _("Gray")
        DarkGray = "Preset13", _("Dark Gray")
        Black = "Preset14", _("Black")
        DarkRed = "Preset15", _("Dark Red")
        DarkOrange = "Preset16", _("Dark Orange")
        DarkBrown = "Preset17", _("Dark Brown")
        DarkYellow = "Preset18", _("Dark Yellow")
        DarkGreen = "Preset19", _("Dark Green")
        DarkTeal = "Preset20", _("Dark Teal")
        DarkOlive = "Preset21", _("Dark Olive")
        DarkBlue = "Preset22", _("Dark Blue")
        DarkPurple = "Preset23", _("Dark Purple")
        DarkCranberry = "Preset24", _("Dark Cranberry")

    account_outlook_setting = models.ForeignKey(
        AccountOutlookSetting,
        verbose_name=_("account Outlook setting"),
        related_name="outlook_categories",
        on_delete=models.CASCADE,
        null=False)

    # UUID from MSGraph category creation
    # We'll only ever need it in str format, so no need for UUID field.
    category_uuid = models.CharField(max_length=36,
                                     null=False,
                                     blank=False,
                                     verbose_name=_("category UUID")
                                     )

    category_name = models.CharField(
        max_length=256,
        verbose_name=_("category name"),
        default="OSdatascanner Match",
        null=False,
        blank=False)

    category_colour = models.CharField(
        max_length=10,
        choices=OutlookCategoryColour.choices,
        verbose_name=_("category colour"),
        default=OutlookCategoryColour.DarkRed)

    class OutlookCategoryNames(models.TextChoices):
        MATCH = "match", _("match")
        FALSE_POSITIVE = "false_positive", _("false positive")

    name = models.CharField(
        max_length=20,
        verbose_name=_("name"),
        choices=OutlookCategoryNames.choices,
        default=OutlookCategoryNames.MATCH,
        null=False,
        blank=False)

    class Meta:
        constraints = [
            # Don't allow multiple settings with the same category for the same account
            models.UniqueConstraint(
                fields=[
                    'name',
                    'account_outlook_setting'],
                name='outlook_category_label_type_name_and_outlook_setting_constraint'),
            # Outlook _really_ cares that the name of a label for a user is unique
            # which means we have to care as well.
            models.UniqueConstraint(
                fields=[
                    'category_name',
                    'account_outlook_setting'],
                name='outlook_category_display_name_and_outlook_setting_constraint')
        ]
