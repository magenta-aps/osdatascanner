from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.postgres.search import SearchVector
from django.views.generic import DeleteView
from django.http import Http404, HttpResponseRedirect
from django.urls import reverse_lazy
from django.core.exceptions import ValidationError
from django.forms import ModelForm

from ..models import Account, Alias
from ..models.aliases import AliasType
from ...adminapp.views.views import (RestrictedListView, RestrictedDetailView,
                                     RestrictedCreateView)
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
            qs = qs.annotate(search=SearchVector("username", "first_name", "last_name"))
            qs = qs.filter(search=search)

        return qs

    def order_queryset(self, qs):
        qs = qs.order_by('first_name', 'last_name')
        return qs

    def get_paginate_by(self, queryset):
        # Overrides get_paginate_by to allow changing it in the template
        # as url param paginate_by=xx
        return self.request.GET.get('paginate_by', self.paginate_by)


class AccountDetailView(ClientAdminMixin, RestrictedDetailView):
    model = Account
    template_name = "organizations/account_detail.html"
    context_object_name = "account"
    fields = ()

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

        return self.get(request, *args, **kwargs)


class AliasCreateView(ClientAdminMixin, RestrictedCreateView):
    model = Alias
    template_name = "components/modals/alias_create.html"
    fields = ('_alias_type', '_value')

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
