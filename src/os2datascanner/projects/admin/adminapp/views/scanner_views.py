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

import structlog
from enum import Enum
from json import dumps

from pika.exceptions import AMQPError

from django.db.models import Q
from django.core.exceptions import PermissionDenied
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.forms import ModelMultipleChoiceField, ModelChoiceField
from django.utils.translation import gettext_lazy as _
from django.views.generic.edit import CreateView, UpdateView

from os2datascanner.projects.admin.organizations.models import Organization, Account, Alias
from os2datascanner.projects.admin.utilities import UserWrapper

from .views import RestrictedListView, RestrictedCreateView, \
    RestrictedUpdateView, RestrictedDetailView, RestrictedDeleteView, \
    OrgRestrictedMixin
from ..models.rules import Rule
from ..models.scannerjobs.scanner import Scanner
from ..models.scannerjobs.filescanner import FileScanner
from ..models.scannerjobs.webscanner import WebScanner
from ..models.scannerjobs.exchangescanner import ExchangeScanner
from ..models.scannerjobs.msgraph import (MSGraphFileScanner, MSGraphMailScanner,
                                          MSGraphCalendarScanner, MSGraphTeamsFileScanner,
                                          MSGraphSharepointScanner)
from ..models.scannerjobs.sbsysscanner import SbsysScanner
from ..models.scannerjobs.gmail import GmailScanner
from ..models.scannerjobs.googledrivescanner import GoogleDriveScanner
from ..models.scannerjobs.scanner_helpers import CoveredAccount
from ..utils import CleanAccountMessage
from .utils.remediators import reconcile_remediators
from ...organizations.models.aliases import AliasType

logger = structlog.get_logger("adminapp")


class ScannerViewType(Enum):
    LIST = "list"
    CREATE = "add"
    UPDATE = "update"
    COPY = "copy"
    CLEANUP = "cleanup"


class ScannerList(RestrictedListView):
    """Displays list of scanners."""

    scanner_view_type = ScannerViewType.LIST

    template_name = 'scanners.html'
    context_object_name = 'scanner_list'

    def get_queryset(self):
        qs = super().get_queryset()
        if search_field := self.request.GET.get('search_field'):
            qs = qs.filter(name__icontains=search_field)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["add_scanner_url"] = self.model.get_create_url()
        context = self.add_scanner_tabs(context)
        context["active_tab"] = self.model.get_type()
        return context

    def add_scanner_tabs(self, context):
        scanner_models = [
            WebScanner, FileScanner, ExchangeScanner, MSGraphMailScanner, MSGraphFileScanner,
            MSGraphTeamsFileScanner, MSGraphCalendarScanner, MSGraphSharepointScanner,
            GoogleDriveScanner, GmailScanner, SbsysScanner
        ]

        context["scanner_tabs"] = [scanner for scanner in scanner_models if scanner.enabled()]

        return context


class _FormMixin:
    template_name = "components/forms/grouping_model_form_wrapper.html"

    def get_context_data(self, *args, **kwargs):
        d = super().get_context_data(*args, **kwargs)
        d["scanner_model"] = self.model  # compat
        return d

    def form_valid(self, form):
        rv = super().form_valid(form)
        reconcile_remediators(form.cleaned_data["remediators"], self.object)
        return rv

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()

        # We need to serve the correct organization to the form
        user_orgs = Organization.objects.filter(
                UserWrapper(self.request.user).make_org_Q("uuid")
            )
        requested_org_uuid = self.request.GET.get("organization") \
            or self.request.POST.get("organization")
        if org := user_orgs.filter(uuid=requested_org_uuid).first():
            # A specific organization was requested, and the user has access to it. Use that one.
            pass
        elif self.object:
            # We are updating an existing scanner, grab the organization.
            org = self.object.organization
        else:
            # We are creating a new scanner, grab the first organization we can find
            org = user_orgs.order_by("name").first()

        kwargs.update({"user": self.request.user, "org": org, "this_url": self.request.path})
        return kwargs


class _AdminOnlyMixin:

    def dispatch(self, request, *args, **kwargs):
        # The user is only allowed in if they have access to at least one organization
        if hasattr(request.user, "administrator_for") or request.user.has_perm("core.view_client"):
            return super().dispatch(request, *args, **kwargs)
        else:
            raise PermissionDenied(_("User is not administrator for any client"))


class ScannerCreateDf(PermissionRequiredMixin, _AdminOnlyMixin, LoginRequiredMixin, _FormMixin,
                      CreateView):
    scanner_view_type = ScannerViewType.CREATE
    template_name = "components/forms/grouping_model_form_wrapper.html"
    permission_required = "os2datascanner.add_scanner"


class ScannerUpdateDf(PermissionRequiredMixin, _AdminOnlyMixin, OrgRestrictedMixin, _FormMixin,
                      UpdateView):
    scanner_view_type = ScannerViewType.UPDATE
    edit = True
    template_name = "components/forms/grouping_model_form_wrapper.html"
    permission_required = "os2datascanner.change_scanner"

    def form_valid(self, form):
        """If the user does not have permission to validate a scan, changes made by that user
        must invalidate the scan."""

        # Call the save method, but do not commit to the database.
        # This gives us the object with updated fields.
        self.object = form.save(commit=False)

        # TODO: Only do this if changes have been made.
        # Currently, calling "has_changed" on the Form always returns true because of something
        # weird going on with the RecurrenceField.

        # If the user is not allowed to validate scans ...
        if not self.request.user.has_perm("os2datascanner.can_validate"):
            # ... invalidate the scanner
            self.object.validation_status = Scanner.INVALID

        return super().form_valid(form)

    def get_initial(self):
        return self.initial | {
            "remediators": Account.objects.filter(
                    aliases___alias_type=AliasType.REMEDIATOR.value,
                    aliases___value=str(self.object.pk))
        }


class ScannerCopyDf(PermissionRequiredMixin, _AdminOnlyMixin, LoginRequiredMixin, _FormMixin,
                    CreateView):
    scanner_view_type = ScannerViewType.COPY
    template_name = "components/forms/grouping_model_form_wrapper.html"
    permission_required = "os2datascanner.add_scanner"

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)

    def get_initial(self):
        new_name = self.get_object().name
        while Scanner.objects.unfiltered().filter(name=new_name).exists():
            new_name += " " + _("Copy")

        return super().get_initial() | {
            "remediators": Account.objects.filter(
                    aliases___alias_type=AliasType.REMEDIATOR.value,
                    aliases___value=str(self.get_object().pk)),

            # Copied scannerjobs should be "Invalid" by default
            # to avoid being able to misuse this feature.
            "validation_status": Scanner.INVALID,
            "name": new_name
        }


class ScannerBase(object):
    template_name = 'components/scanner/scanner_form.html'

    fields = [
        'name',
        'schedule',
        'do_ocr',
        'do_last_modified_check',
        'keep_false_positives',
        'only_notify_superadmin',
        'rule',
        'exclusion_rule',
        'organization',
        'contacts',
    ]

    def get_form(self, form_class=None):
        """Get the form for the view.

        Querysets used for choices in the 'domains' and 'rule' fields
        will be limited by the user's organization unless the user is a
        superuser.
        """

        form = super().get_form(form_class)
        user = UserWrapper(self.request.user)

        form.fields['schedule'].required = False
        org_qs = Organization.objects.filter(user.make_org_Q("uuid"))
        form.fields['organization'].queryset = org_qs
        form.fields['organization'].empty_label = None

        selected_org = self.get_selected_org(org_qs)

        form.fields['organization'].initial = selected_org

        allowed_rules = Rule.objects.filter(
            Q(organization__in=org_qs) | Q(organization__isnull=True, organizations=selected_org))

        form.fields["rule"] = ModelChoiceField(
            allowed_rules,
            validators=ModelMultipleChoiceField.default_validators,
        )

        form.fields["exclusion_rule"] = ModelChoiceField(
            allowed_rules,
            validators=ModelMultipleChoiceField.default_validators,
            required=False
        )

        return form

    def get_selected_org(self, org_qs):
        return self.get_object().organization or \
            org_qs.filter(pk=self.request.GET.get("organization")).first() or \
            org_qs.first()

    def get_form_fields(self):
        """Get the list of form fields.

        The 'validation_status' field will be added to the form if the
        user has permission to validate scanners.
        """
        fields = super().get_form_fields()
        if self.request.user.has_perm('os2datascanner.can_validate'):
            fields.append('validation_status')

        self.fields = fields
        return fields

    def filter_queryset(self, form, organization):
        for field_name in ['rule', 'exclusion_rule']:
            queryset = form.fields[field_name].queryset
            queryset = queryset.filter(organization=organization)
            form.fields[field_name].queryset = queryset

    def get_scanner_object(self):
        return self.get_object()

    def create_remediator_aliases(self, request):
        remediator_uuids = request.POST.getlist('remediators')
        # It is possible to not have an object at this point, eq. if the
        # CreateView form is invalid. In that case, we don't do anything.
        if self.object:
            # Delete old remediators from this scanner, if they are no longer
            # specified in the form.
            Alias.objects.filter(
                _alias_type=AliasType.REMEDIATOR,
                _value=self.object.pk).exclude(
                account__uuid__in=remediator_uuids).delete()
            # Create new remediator aliases
            for remediator_uuid in remediator_uuids:
                Alias.objects.get_or_create(
                    account=Account.objects.get(uuid=remediator_uuid),
                    _alias_type=AliasType.REMEDIATOR,
                    _value=self.object.pk)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = UserWrapper(self.request.user)
        orgs = Organization.objects.filter(user.make_org_Q("uuid"))

        selected_org = self.get_selected_org(orgs)

        context["scanner_model"] = self.model

        if self.object:
            context["remediators"] = self.object.get_remediators()
        context["possible_remediators"] = Account.objects.filter(organization=selected_org).exclude(
            Q(aliases___alias_type=AliasType.REMEDIATOR) & Q(aliases___value=0))
        context["universal_remediators"] = Account.objects.filter(Q(organization=selected_org) & Q(
            aliases___alias_type=AliasType.REMEDIATOR) & Q(aliases___value=0))

        context["possible_contacts"] = get_user_model().objects.filter(
            Q(administrator_for__client=selected_org.client) |
            Q(groups__permissions__codename="view_client") |
            Q(user_permissions__codename="view_client") |
            Q(is_superuser=True)
        ).distinct()

        context["supports_rule_preexec"] = getattr(
                self.model, "supports_rule_preexec", False)

        return context

    def dispatch(self, request, *args, **kwargs):
        # The user is only allowed in if they have access to at least one organization
        if hasattr(request.user, "administrator_for") or request.user.has_perm("core.view_client"):
            return super().dispatch(request, *args, **kwargs)
        else:
            raise PermissionDenied(_("User is not administrator for any client"))

    def form_valid(self, form):
        data = form.cleaned_data
        if 'org_units' in data and 'scan_entire_org' in data:
            # This scanner scans based on org units
            # The user should have either chosen some org units, or chosen to scan the entire org
            if not data['org_units'].exists() and not data.get('scan_entire_org', False):
                form.add_error("org_units",
                               _("You should either choose organizational units to scan, "
                                 "or choose to scan the entire organization."))
                return super().form_invalid(form)
        return super().form_valid(form)


class ScannerCreate(PermissionRequiredMixin, ScannerBase, RestrictedCreateView):
    """View for creating a new scannerjob."""
    scanner_view_type = ScannerViewType.CREATE

    permission_required = "os2datascanner.add_scanner"

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        self.create_remediator_aliases(request)
        return response

    def get_selected_org(self, org_qs):
        return org_qs.filter(pk=self.request.GET.get("organization")).first() or org_qs.first()


class ScannerUpdate(PermissionRequiredMixin, ScannerBase, RestrictedUpdateView):
    """View for editing an existing scannerjob."""
    scanner_view_type = ScannerViewType.UPDATE

    permission_required = "os2datascanner.change_scanner"
    old_url = ''
    old_rule = None
    edit = True

    def get_form(self, form_class=None):
        """Get the form for the view.

        Queryset used for choices in the 'rule' field
        will be limited by the user's organization unless the user is a
        superuser.
        """
        form = super().get_form(form_class)
        self.object = self.get_object()
        if hasattr(self.object, "url"):
            self.old_url = self.object.url
        elif hasattr(self.object, "mail_domain"):
            self.old_url = self.object.mail_domain
        elif hasattr(self.object, "unc"):
            self.old_url = self.object.unc
        # Store the existing rule selected in the scannerjob
        self.old_rule = self.object.rule

        return form

    def get_form_fields(self):
        return super().get_form_fields()

    def form_valid(self, form):
        """Validate the submitted form."""

        # Saving the object instance here without committing to the db to check for revalidation
        self.object = form.save(commit=False)

        if not self.request.user.has_perm("os2datascanner.can_validate"):
            self.object.validation_status = Scanner.INVALID

        def is_in_cleaned(entry, comparable):
            data = form.cleaned_data
            return entry in data and data[entry] != comparable

        return super().form_valid(form)

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        self.create_remediator_aliases(request)
        return response


class ScannerRemove(PermissionRequiredMixin, RestrictedDeleteView):
    permission_required = "os2datascanner.hide_scanner"

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.hide(hidden_by=request.user)

        messages.add_message(
                request,
                messages.SUCCESS,
                _("The scannerjob was removed."),
                extra_tags="manual_close"
            )

        return redirect(self.get_success_url())


class ScannerDelete(PermissionRequiredMixin, RestrictedDeleteView):
    permission_required = "os2datascanner.delete_scanner"
    fields = []

    def get_form(self, form_class=None):
        if form_class is None:
            form_class = self.get_form_class()

        return super().get_form(form_class)

    def form_valid(self, form):
        response = super().form_valid(form)

        # TODO: Despite the superclass calling either this method or `form_invalid`, neither seems
        # to be called ...

        messages.add_message(
                self.request,
                messages.SUCCESS,
                _("The scannerjob was deleted."),
                extra_tags="manual_close"
            )

        return response

    def form_invalid(self, *args, **kwargs):
        response = super().form_invalid(*args, **kwargs)

        # TODO: Despite the superclass calling either this method or `form_valid`, neither seems
        # to be called ...

        messages.add_message(
                self.request,
                messages.WARNING,
                _("The scannerjob was not removed!"),
                extra_tags="manual_close"
            )

        return response


class ScannerCopy(PermissionRequiredMixin, ScannerBase, RestrictedCreateView):
    """Creates a copy of an existing scanner. """
    scanner_view_type = ScannerViewType.COPY

    permission_required = "os2datascanner.add_scanner"

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        self.create_remediator_aliases(request)
        return response

    def get_initial(self):
        initial = super().get_initial()

        scanner_obj = ScannerUpdate.get_scanner_object(self)

        # Copied scannerjobs should be "Invalid" by default
        # to avoid being able to misuse this feature.
        initial["validation_status"] = Scanner.INVALID
        while Scanner.objects.unfiltered().filter(name=scanner_obj.name).exists():
            scanner_obj.name += " " + _("Copy")
        initial["name"] = scanner_obj.name

        return initial


class ScannerAskRun(RestrictedDetailView):
    """Base class for prompt before starting scan, validate first."""
    fields = []
    context_object_name = "scanner"
    template_name = 'components/scanner/scanner_ask_run.html'
    run_url_name = ""

    def get_context_data(self, **kwargs):
        """Check that user is allowed to run this scanner."""
        context = super().get_context_data(**kwargs)
        last_status = self.object.statuses.last()
        error_message = ""
        if self.object.validation_status is Scanner.INVALID:
            ok = False
            error_message = Scanner.NOT_VALIDATED
        elif not self.object.rule:
            ok = False
            error_message = Scanner.HAS_NO_RULES
        elif last_status and last_status.is_running:
            ok = False
            error_message = Scanner.ALREADY_RUNNING
        else:
            ok = True

        context["partial_scan"] = (self.object.do_last_modified_check and
                                   self.object.statuses.exists())

        context["ok"] = ok

        if not ok:
            context['error_message'] = error_message

        context["run_redirect"] = self.get_run_redirect()

        return context

    def get_run_redirect(self):
        return reverse_lazy(self.run_url_name, kwargs={'pk': self.kwargs.get('pk')})


class ScannerRun(RestrictedDetailView):
    """Base class for view that handles starting of a scanner run."""

    fields = []
    template_name = 'components/scanner/scanner_run.html'
    model = Scanner

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        full_scan = self.request.GET.get("full", False) == "true"

        try:
            context['scan_tag'] = dumps(
                self.object.run(user=self.request.user, force=full_scan), indent=2)
        except Exception as ex:
            logger.error("Error while starting ScannerRun", exc_info=True)
            error_type = type(ex).__name__
            if isinstance(ex, AMQPError):
                context['pika_error'] = f"pika failure [{error_type}]"
            else:
                context['engine2_error'] = f"Engine failure [{error_type}]."
                context['engine2_error'] += ", ".join([str(e) for e in ex.args])

        return context


class ScannerCleanupStaleAccounts(RestrictedDetailView):
    """Base class for view that handles cleaning up stale accounts
    associated with a scanner."""

    scanner_view_type = ScannerViewType.CLEANUP

    fields = []
    template_name = 'components/scanner/scanner_cleanup_stale_accounts.html'
    model = Scanner
    context_object_name = 'scanner'

    @property
    def scanner_running(self):
        return (self.object.statuses.last() and self.object.statuses.last().is_running)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.is_htmx = request.headers.get('HX-Request') == "true"
        uuids_to_clean = request.POST.getlist('cleanup_account_uuids', [])

        if not self.is_htmx:
            return

        if request.headers.get('HX-Trigger-Name') == "cleanup-button":

            if not self.scanner_running:
                stale_accounts = self.object.compute_stale_accounts()

                clean_dict = {
                    self.object.pk: (
                            acc_dict := CleanAccountMessage.make_account_dict(
                                    acc for acc in stale_accounts
                                    if str(acc.uuid) in uuids_to_clean))
                }

                logger.info(
                        "Cleaning up accounts:"
                        f" {', '.join(acc_dict['usernames'])}"
                        f" for scanner: {self.object}.")

                CleanAccountMessage.send(clean_dict, publisher="UI-manual")

                # When we send CleanAccountMessages, the report module deletes all of
                # the matches associated with these accounts, but the admin
                # system still knows about them; delete that knowledge to make
                # sure we don't have uncovered periods
                CoveredAccount.objects.filter(
                        scanner=self.object,
                        account_id__in=acc_dict["uuids"]).delete()
            return render(
                request,
                "components/scanner/scanner_cleanup_response.html",
                context=self.get_context_data())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["running"] = self.scanner_running
        return context


class RemovedScannersView(PermissionRequiredMixin, ScannerList):
    """View for listing all removed scanners."""
    template_name = "removed_scanners.html"
    model = Scanner
    queryset = Scanner.objects.unfiltered().filter(hidden=True)
    permission_required = "os2datascanner.view_hidden_scanner"

    def get_queryset(self):
        return super().get_queryset().select_subclasses()

    def get_context_data(self, **kwargs):
        # Do not inherit from ScannerList, but from ScannerList's parent class instead.
        # This method in ScannerList tries to fetch the url to the create view for the current
        # scanner type. However, this view does not represent a scanner type, but rather points
        # to the base `Scanner` model. Trying to fetch the create url for `Scanner` does not work.
        context = super(ScannerList, self).get_context_data(**kwargs)
        context = self.add_scanner_tabs(context)
        context["active_tab"] = "removed"
        return context


class RecreateScannerView(PermissionRequiredMixin, RestrictedUpdateView):
    permission_required = "os2datascanner.unhide_scanner"
    model = Scanner

    def get_success_url(self):
        return reverse_lazy("removed_scanners")

    def get_queryset(self):
        return Scanner.objects.unfiltered().filter(hidden=True)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.unhide()

        messages.add_message(
                request,
                messages.SUCCESS,
                _("The scannerjob was recreated."),
                extra_tags="manual_close"
            )

        return redirect(self.get_success_url())


class DeleteRemovedScannerView(ScannerDelete):
    """A separate view is required for this, since the regular view cannot access hidden
    scanners."""
    queryset = Scanner.objects.unfiltered().filter(hidden=True)
    success_url = reverse_lazy("removed_scanners")
