from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.postgres.search import TrigramSimilarity
from django.views.generic import DetailView, CreateView, DeleteView
from django.http import Http404, HttpResponseRedirect
from django.urls import reverse_lazy
from django.core.exceptions import ValidationError, PermissionDenied
from django.forms import ModelForm
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _
from django.db.models.functions import Concat, Greatest
from django.db.models import CharField, Value, Max
from django.contrib.auth.models import Permission

from ..models import Account, Alias, OrganizationalUnit, SyncedPermission
from ..models.aliases import AliasType
from ...adminapp.views.views import RestrictedListView
from ...adminapp.models.scannerjobs.scanner import Scanner
from ...adminapp.views.scanner_views import EmptyPagePaginator
from ..utils import ClientAdminMixin


class AccountListView(ClientAdminMixin, RestrictedListView):
    model = Account
    paginator_class = EmptyPagePaginator
    paginate_by = 10
    template_name = "organizations/account_list.html"
    context_object_name = "accounts"
    paginate_by_options = [10, 25, 50, 100, 250]

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
            qs = qs.annotate(
                full_name=Concat('first_name', Value(' '), 'last_name',
                                 output_field=CharField())
            ).annotate(
                search=Greatest(
                    TrigramSimilarity("full_name", search),
                    TrigramSimilarity("username", search)
                )
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
                    acc.save()
                else:
                    raise PermissionDenied("User does not have the 'change_permissions_account'"
                                           "-permission.")

            case 'rem-permission':
                if request.user.has_perm('organizations.change_permissions_account'):
                    removed_permission = request.POST.get('rem-permission')

                    acc.permissions.remove(removed_permission)
                    acc.save()
                else:
                    raise PermissionDenied("User does not have the 'change_permissions_account'"
                                           "-permission.")

            case _:
                raise PermissionDenied(f"View called from unknown source: {trigger_name}")

        return self.get(request, *args, **kwargs)


class AliasCreateView(LoginRequiredMixin, ClientAdminMixin, CreateView):
    model = Alias
    template_name = "components/modals/alias_create.html"
    fields = ('_alias_type', '_value', 'shared')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["organization"] = self.kwargs['org']
        context["account"] = Account.objects.get(uuid=self.kwargs.get('acc_uuid'))
        return context

    def form_valid(self, form: ModelForm):
        form.instance.account = Account.objects.get(uuid=self.kwargs.get('acc_uuid'))
        try:
            form.instance.value = form.cleaned_data['_value']
        except ValidationError as e:
            messages.error(self.request, e.message)
            return self.form_invalid(form)
        return super().form_valid(form)

    def form_invalid(self, form):
        return HttpResponseRedirect(
            reverse_lazy(
                'account',
                kwargs={
                    'org_slug': self.kwargs.get('org').slug,
                    'pk': self.kwargs.get('acc_uuid')}))

    def get_success_url(self):
        return reverse_lazy(
            'account',
            kwargs={
                'org_slug': self.kwargs.get('org_slug'),
                'pk': self.kwargs.get('acc_uuid')})


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
