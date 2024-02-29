import requests
import structlog
from django.core.exceptions import PermissionDenied
from django.db import models
from django.conf import settings
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from .account import Account
from os2datascanner.projects.report.reportapp.views.utilities.msgraph_utilities import (
    OutlookCategoryName, get_msgraph_mail_document_reports,
    get_mail_message_handle_from_document_report)
from os2datascanner.core_organizational_structure.models.organization import (
    OutlookCategorizeChoices)

logger = structlog.get_logger()


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

    def populate_setting(self):  # noqa: CCR001 Too complex
        def _create_category(owner, category_name, category_colour):
            try:
                response = gc.create_outlook_category(
                    owner, category_name=category_name,
                    category_colour=category_colour
                )
                if response.ok:
                    logger.info(f"Successfully created Outlook Category for {owner}! "
                                f"Category name: {category_name} & Colour {category_colour}")
                    return response.json().get("id")

            except requests.HTTPError as ex:
                if ex.response.status_code == 409:  # Conflict / Already exists
                    try:
                        master_categories = gc.paginated_get(
                            f"users/{owner}/outlook/masterCategories")
                        for category in master_categories:
                            if category.get("displayName") == category_name:
                                logger.info("Found existing category! Fetching ID..")
                                return category.get("id")
                    except requests.HTTPError as ex:
                        logger.warning(f"Couldn't fetch existing category! "
                                       f"Got response: {ex.response}")

                else:
                    logger.warning(f"Couldn't create category! Got response: {ex.response}")
                    return None

        # Only objects that don't have either a match or fp category are relevant for inspection.
        qs = self.filter(
            Q(match_category_uuid__isnull=True) | Q(false_positive_category_uuid__isnull=True)
        )

        with requests.Session() as session:
            gc = self._initiate_graphcaller(session)

            for outl_setting in qs:
                # TODO: ENUM use should be refactored to support name change.
                if not outl_setting.match_category_uuid:
                    match_uuid = _create_category(outl_setting.account.username,
                                                  OutlookCategoryName.Match.value,
                                                  outl_setting.match_colour)
                    outl_setting.match_category_uuid = match_uuid
                if not outl_setting.false_positive_category_uuid:
                    fp_uuid = _create_category(outl_setting.account.username,
                                               OutlookCategoryName.FalsePositive.value,
                                               outl_setting.false_positive_colour)
                    outl_setting.false_positive_category_uuid = fp_uuid

                # TODO: Perhaps convert to bulk updates
                outl_setting.categorize_email = True
                outl_setting.save()
                logger.info(f"Saved {outl_setting}")

    def categorize_existing(self):  # noqa: CCR001 Too complex

        qs = self.select_related("account")
        with requests.Session() as session:
            gc = self._initiate_graphcaller(session)

            for outl_setting in qs:
                doc_reps = []
                # TODO: this is weird.. having to encapsulate in try except to do a filter.
                try:
                    doc_reps = get_msgraph_mail_document_reports(outl_setting.account)
                except PermissionDenied:
                    logger.info(f"No msgraph-mail document reports for {outl_setting.account}")

                for doc_rep in doc_reps:
                    message_handle = get_mail_message_handle_from_document_report(doc_rep)
                    msg_id = message_handle.relative_path if message_handle else None
                    try:
                        existing_categories_response = gc.get(
                            f"users/{outl_setting.account.username}/messages/{msg_id}?$select"
                            f"=categories").json()

                        email_categories = existing_categories_response.get("categories", [])

                        # Only append if it isn't already marked.
                        # TODO: refactor to not use ENUM
                        if not any(category.value in email_categories for category in
                                   OutlookCategoryName):
                            email_categories.append(OutlookCategoryName.Match.value)

                        categorize_email_response = gc.categorize_mail(
                            outl_setting.account.username,
                            msg_id,
                            email_categories)

                        if categorize_email_response.ok:
                            logger.info(f"Successfully added category "
                                        f"{OutlookCategoryName.Match.value} to email for: "
                                        f"{outl_setting.account.username}!")

                    except requests.HTTPError as ex:
                        # We don't want to raise anything here, as we're iterating emails.
                        # The most likely scenario is just that the mail doesn't exist anymore.
                        logger.warning(f"Couldn't categorize email! Got response: {ex.response}")

    def update_colour(self, match_colour, fp_colour):
        with requests.Session() as session:
            gc = self._initiate_graphcaller(session)

            for outl_setting in self:
                try:
                    if outl_setting.match_colour != match_colour:
                        match_resp = gc.update_category_colour(
                            outl_setting.account.username,
                            outl_setting.match_category_uuid,
                            match_colour)

                        if match_resp.ok:
                            logger.info(f"Updated Match colour to {match_colour}!")

                    if outl_setting.false_positive_colour != fp_colour:
                        fp_resp = gc.update_category_colour(
                            outl_setting.account.username,
                            outl_setting.false_positive_category_uuid,
                            fp_colour)

                        if fp_resp.ok:
                            logger.info(f"Updated False Positive colour to {fp_colour}!")

                except requests.HTTPError as ex:
                    logger.warning(f"Couldn't update colour! Got response: {ex.response}")

            # Update database
            self.update(match_colour=match_colour, false_positive_colour=fp_colour)

    def delete_categories(self):
        with requests.Session() as session:
            gc = self._initiate_graphcaller(session)
            for outl_setting in self:
                try:
                    delete_match_category_response = gc.delete_category(
                        outl_setting.account.username,
                        outl_setting.match_category_uuid)
                    if delete_match_category_response.ok:
                        logger.info(f"Successfully deleted Match "
                                    f"Outlook Category for {outl_setting.account}! ")

                    delete_fp_response = gc.delete_category(
                        outl_setting.account.username,
                        outl_setting.false_positive_category_uuid)
                    if delete_fp_response.ok:
                        logger.info(f"Successfully deleted False Positive "
                                    f"Outlook Category for {outl_setting.account}! ")

                except requests.HTTPError as ex:
                    logger.warning(f"Couldn't delete category! Got response: {ex.response}")

            # Update database
            self.update(categorize_email=False,
                        match_category_uuid=None,
                        false_positive_category_uuid=None)

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

    objects = AccountOutlookSettingQuerySet.as_manager()

    account = models.OneToOneField(Account,
                                   on_delete=models.CASCADE,
                                   related_name="outlook_settings")

    categorize_email = models.BooleanField(default=False,
                                           verbose_name=_("Categorize emails"))

    # UUID from MSGraph category creation
    # We'll only ever need it in str format, so no need for UUID field.
    match_category_uuid = models.CharField(max_length=36,
                                           null=True,
                                           blank=True,
                                           )

    match_colour = models.CharField(max_length=10,
                                    choices=OutlookCategoryColour.choices,
                                    verbose_name=_("Category colour for matches"),
                                    default=OutlookCategoryColour.DarkRed,
                                    )

    false_positive_category_uuid = models.CharField(max_length=36,
                                                    null=True,
                                                    blank=True,
                                                    )

    false_positive_colour = models.CharField(max_length=10,
                                             choices=OutlookCategoryColour.choices,
                                             verbose_name=_("Category colour for false positives"),
                                             default=OutlookCategoryColour.DarkGreen)
