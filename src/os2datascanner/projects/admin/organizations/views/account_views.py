# Part of the OSdatascanner system, copyright © 2014-2026 Magenta ApS.
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, you can
# obtain one at http://mozilla.org/MPL/2.0/.

from typing import override

import structlog

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.postgres.search import TrigramSimilarity
from django.views.generic import DetailView, CreateView, DeleteView
from django.http import Http404, HttpResponse, HttpResponseBadRequest
from django.urls import reverse_lazy
from django.core.exceptions import ValidationError, PermissionDenied
from django.forms import ModelForm
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _
from django.db.models.functions import Coalesce, Concat, Greatest
from django.db.models import CharField, Value, Max, Q, OuterRef, Subquery, Count
from django.contrib.auth.models import Permission
from django import forms
from django.db import IntegrityError, transaction

from ..models import Account, Alias, OrganizationalUnit, SyncedPermission
from ..models.aliases import AliasType
from ...adminapp.views.views import RestrictedListView
from ...adminapp.models.scannerjobs.scanner import Scanner
from os2datascanner.projects.utils.pagination import EmptyPagePaginator
from ..utils import ClientAdminMixin

logger = structlog.get_logger("admin_organizations")


def search_accounts(qs, search, fields=("full_name", "username")):
    """Fuzzy-matches accounts against search, annotating each result with its
    best trigram similarity as 'search' """
    qs = qs.annotate(
        full_name=Concat('first_name', Value(' '), 'last_name',
                         output_field=CharField())
    ).annotate(
        search=Greatest(*(TrigramSimilarity(field, search) for field in fields))
    ).exclude(search=0)
    if qs.exists():
        max_similarity = qs.aggregate(Max("search", default=0))['search__max']
        # We only want accounts whose similarity to the search word is at least,
        # 0.3 times as similar as the most similar one.
        # As such a user won't recieve an empty list of results.
        # 0.3 has been chosen, as this threshold should include all instances of a name,
        # including different spellings, such as "Christopher", "Cristofer", etc.
        qs = qs.filter(search__gte=max_similarity * 0.3)
    return qs


class AccountListView(ClientAdminMixin, RestrictedListView):
    model = Account
    paginator_class = EmptyPagePaginator
    paginate_by = 10
    template_name = "organizations/account_list.html"
    context_object_name = "accounts"
    paginate_by_options = [10, 25, 50, 100, 250]
    search_fields = ("full_name", "username")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["organization"] = self.kwargs['org']
        context['paginate_by'] = int(self.request.GET.get('paginate_by', self.paginate_by))
        context['paginate_by_options'] = self.paginate_by_options
        return context

    def get_queryset(self):
        qs = super().get_queryset()

        org = self.kwargs['org']

        qs = qs.filter(organization=org)

        qs = self.search_queryset(qs)

        qs = self.order_queryset(qs)

        return qs

    def search_queryset(self, qs):
        if search := self.request.GET.get('search_field'):
            qs = search_accounts(qs, search, self.search_fields)
        return qs

    def order_queryset(self, qs):
        if self.request.GET.get('search_field'):
            qs = qs.order_by('-search', 'first_name', 'last_name')
        else:
            qs = qs.order_by('first_name', 'last_name')
        return qs

    def get_paginate_by(self, queryset):
        # Overrides get_paginate_by to allow changing it in the template
        # as url param paginate_by=xx
        return self.request.GET.get('paginate_by', self.paginate_by)


class AccountDetailView(LoginRequiredMixin, ClientAdminMixin, DetailView):
    model = Account
    template_name = "organizations/account_detail.html"
    context_object_name = "account"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["imported_aliases"] = self.object.aliases.exclude(
            _alias_type=AliasType.REMEDIATOR).filter(imported=True)
        context["other_aliases"] = self.object.aliases.exclude(
            _alias_type=AliasType.REMEDIATOR).filter(imported=False)
        context["remediator_for_scanners"] = self.object.get_remediator_scanners()
        existing_pks = [scanner.get('pk') for scanner in context["remediator_for_scanners"]]
        context["scanners"] = list(Scanner.objects.filter(organization=self.kwargs['org'])
                                   .exclude(pk__in=existing_pks)
                                   .values('name', 'pk'))
        context["permissions"] = Permission.objects.filter(
                content_type__app_label=SyncedPermission._meta.app_label,
                content_type__model=SyncedPermission._meta.model_name
            ).exclude(codename__in=[
                "add_syncedpermission",
                "delete_syncedpermission",
                "change_syncedpermission",
                "view_syncedpermission"
            ]).exclude(pk__in=self.object.permissions.values_list("pk", flat=True))
        return context

    def post(self, request, *args, **kwargs):
        trigger_name = request.headers.get('HX-Trigger-Name')

        acc = self.get_object()

        match trigger_name:
            case 'remediator-check':
                if request.POST.get('remediator-check', False) == 'on':
                    # Create a universal remediator alias
                    Alias.objects.create(account=acc, _alias_type=AliasType.REMEDIATOR, _value=0)
                else:
                    # Delete all universal remediator aliases for the account
                    Alias.objects.filter(
                        account=acc,
                        _alias_type=AliasType.REMEDIATOR,
                        _value=0).delete()

            case 'add-remediator':
                added_scanner_job_pk = request.POST.get('add-remediator')
                org = self.kwargs.get('org')

                # Make sure the scanner and the account belong to the same organization
                if int(added_scanner_job_pk) not in \
                        Scanner.objects.filter(organization=org).values_list('pk', flat=True):
                    raise Http404()

                Alias.objects.create(_alias_type=AliasType.REMEDIATOR,
                                     _value=added_scanner_job_pk,
                                     account=acc)

            case 'rem-remediator':
                removed_scanner_job_pk = request.POST.get('rem-remediator')

                Alias.objects.filter(_alias_type=AliasType.REMEDIATOR,
                                     _value=removed_scanner_job_pk,
                                     account_id=acc).delete()

            case 'add-permission':
                if request.user.has_perm('organizations.change_permissions_account'):
                    added_permission = request.POST.get('add-permission')

                    acc.permissions.add(added_permission)
                else:
                    raise PermissionDenied("User does not have the 'change_permissions_account'"
                                           "-permission.")

            case 'rem-permission':
                if request.user.has_perm('organizations.change_permissions_account'):
                    removed_permission = request.POST.get('rem-permission')

                    acc.permissions.remove(removed_permission)
                else:
                    raise PermissionDenied("User does not have the 'change_permissions_account'"
                                           "-permission.")

            case _:
                raise PermissionDenied(f"View called from unknown source: {trigger_name}")

        return self.get(request, *args, **kwargs)


class AliasForm(forms.ModelForm):
    value = forms.CharField(max_length=256)
    alias_choices = list(AliasType.choices)
    alias_choices.remove((AliasType.REMEDIATOR.value, AliasType.REMEDIATOR.label), )

    alias_type = forms.ChoiceField(choices=[("", "----")] + alias_choices)

    class Meta:
        model = Alias
        fields = ('alias_type', 'value', 'shared')

    def clean(self):
        cleaned_data = super().clean()
        alias_type = cleaned_data.get('alias_type')
        value = cleaned_data.get('value')
        try:
            self.instance._alias_type = alias_type
            self.instance.value = value
        except ValidationError as e:
            self.add_error("value", e)

        return cleaned_data


class AliasCreateView(LoginRequiredMixin, ClientAdminMixin, CreateView):
    model = Alias
    form_class = AliasForm
    template_name = "components/modals/alias_create.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["organization"] = self.kwargs['org']
        context["account"] = Account.objects.get(uuid=self.kwargs.get('acc_uuid'))

        context["AliasType"] = (ac := list(AliasType))
        # Remediator associations are created through scanner jobs, not here
        ac.remove(AliasType.REMEDIATOR)

        return context

    def form_valid(self, form: ModelForm):
        form.instance.account = Account.objects.get(uuid=self.kwargs.get('acc_uuid'))
        try:
            form.save()
            messages.add_message(
                self.request,
                messages.SUCCESS,
                _("Alias created!"),
                extra_tags="auto_close"
            )

            response = HttpResponse()

            response['HX-Redirect'] = reverse_lazy(
                'account',
                kwargs={
                    'org_slug': self.kwargs.get('org_slug'),
                    'pk': self.kwargs.get('acc_uuid')})

            return response
        except IntegrityError:
            form.add_error('value', _("Alias with this value already exists"))
            return self.form_invalid(form)


class AliasDeleteView(LoginRequiredMixin, ClientAdminMixin, DeleteView):
    model = Alias

    def get_success_url(self):
        return reverse_lazy(
            'account',
            kwargs={
                'org_slug': self.kwargs.get('org_slug'),
                'pk': self.kwargs.get('acc_uuid')})


class AccountDropdownView(ClientAdminMixin, RestrictedListView):
    model = Account
    template_name = 'components/dpo_manager_dropdown.html'
    context_object_name = "accounts"

    label = _("Choose Account")
    element_name = "add-account"

    def accounts_to_exclude(self, orgunit):
        return []

    def get_queryset(self, **kwargs):
        qs = super().get_queryset(**kwargs)

        org = self.kwargs['org']
        orgunit = get_object_or_404(OrganizationalUnit, organization=org, pk=self.kwargs['pk'])

        return qs.filter(
            organization=org).difference(
            self.accounts_to_exclude(orgunit)).order_by(
            "first_name",
            "last_name")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        org = self.kwargs['org']
        orgunit = get_object_or_404(OrganizationalUnit, organization=org, pk=self.kwargs['pk'])
        context['orgunit'] = orgunit
        context['label'] = self.label
        context['element_name'] = self.element_name
        return context


class ManagerDropdownView(AccountDropdownView):
    label = _("Choose new manager")
    element_name = "add-manager"

    def accounts_to_exclude(self, orgunit):
        return orgunit.get_managers()


class DPODropdownView(AccountDropdownView):
    label = _("Choose new DPO")
    element_name = "add-dpo"

    def accounts_to_exclude(self, orgunit):
        return orgunit.get_dpos()


class OrgDPODropdownView(ClientAdminMixin, RestrictedListView):
    model = Account
    template_name = 'components/uni_dpo_dropdown.html'
    context_object_name = "uni_dpo_accounts"

    def get_queryset(self, **kwargs):
        qs = super().get_queryset(**kwargs)
        return qs.filter(
            organization=self.kwargs['org'],
            is_universal_dpo=False).order_by(
            "first_name",
            "last_name")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class ManageSharedAccountListView(AccountListView):
    template_name = "organizations/manage_shared_account_list.html"
    context_object_name = "shared_accounts"
    search_fields = AccountListView.search_fields + ("email",)
    queryset = Account.objects.filter(is_shared=True)

    @override
    def get_queryset(self):
        shared_alias_count = Alias.objects.filter(
            account__organization=OuterRef("organization"),
            account__is_shared=False,
            _alias_type=AliasType.EMAIL,
            shared=True,
            _value__iexact=OuterRef("email"),
        ).order_by().values("account__organization").annotate(n=Count("pk")).values("n")

        return super().get_queryset().annotate(
            access_count=Coalesce(Subquery(shared_alias_count), 0))


class SharedAccessForm(forms.Form):
    accounts = forms.ModelMultipleChoiceField(
        queryset=Account.objects.none(), to_field_name="uuid", required=False)

    def __init__(self, *args, candidates, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["accounts"].queryset = candidates


class ManageSharedAccessView(LoginRequiredMixin, ClientAdminMixin, DetailView):
    """Grants accounts access to a shared mailbox's results by giving them a
    shared email alias with the mailbox's address."""
    model = Account
    pk_url_kwarg = "acc_uuid"
    template_name = "components/modals/manage_shared_access.html"
    context_object_name = "shared_account"
    max_search_results = 15

    def get_queryset(self):
        return Account.objects.filter(
            organization=self.kwargs['org'], is_shared=True).exclude(Q(email=None) | Q(email=""))

    def shared_aliases(self):
        return Alias.objects.filter(
            account__organization=self.kwargs['org'],
            account__is_shared=False,
            _alias_type=AliasType.EMAIL,
            _value__iexact=self.object.email,
            shared=True)

    def candidates(self):
        return Account.objects.filter(organization=self.kwargs['org'], is_shared=False)

    def members(self):
        return self.candidates().filter(aliases__in=self.shared_aliases()).distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context |= {
            "organization": self.kwargs['org'],
            "modal_id": f"shared-access-{self.object.uuid}",
            "close_label": _("Close without saving access."),
        }

        if "search_field" in self.request.GET:
            form = SharedAccessForm(self.request.GET, candidates=self.candidates())
            selected = (form.cleaned_data["accounts"] if form.is_valid()
                        else self.candidates().none())
        else:
            selected = self.members()
        context["selected_accounts"] = selected.order_by("first_name", "last_name")

        if search := self.request.GET.get("search_field"):
            results = search_accounts(
                self.candidates().exclude(uuid__in=selected.values("uuid")), search
            ).order_by("-search", "first_name", "last_name")
            context["search_results"] = results[:self.max_search_results]
            context["search_result_count"] = results.count()

        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = SharedAccessForm(request.POST, candidates=self.candidates())
        if not form.is_valid():
            return HttpResponseBadRequest()
        ticked = form.cleaned_data["accounts"]
        members = self.members()

        self.shared_aliases().filter(account__in=members.exclude(uuid__in=ticked)).delete()

        failed = []
        for account in ticked.exclude(uuid__in=members):
            try:
                with transaction.atomic():
                    Alias.objects.create(
                        account=account,
                        _alias_type=AliasType.EMAIL.value,
                        _value=self.object.email,
                        shared=True)
            except IntegrityError:
                # The account already has a non-shared alias with the same value
                logger.warning(
                    "could not create shared alias", account=account.uuid,
                    value=self.object.email, exc_info=True)
                failed.append(account.get_full_name() or account.username)

        match failed:
            case []:
                messages.add_message(
                    request, messages.SUCCESS, _("Access updated!"), extra_tags="auto_close")
            case _:
                messages.add_message(
                    request, messages.WARNING,
                    _("Could not grant access to {names}, as they already have an alias with "
                      "this address.").format(names=", ".join(failed)),
                    extra_tags="manual_close")
        response = HttpResponse()
        response['HX-Redirect'] = reverse_lazy(
            'manage-shared', kwargs={'org_slug': self.kwargs['org_slug']})
        return response
