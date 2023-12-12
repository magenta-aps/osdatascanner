from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import DetailView
from django.shortcuts import get_object_or_404
from django.http import Http404

from ...core.models import Administrator
from ..models import Account, Organization, Alias
from ..models.aliases import AliasType
from ...adminapp.views.views import RestrictedListView
from ...adminapp.models.scannerjobs.scanner import Scanner
from ...adminapp.views.scanner_views import EmptyPagePaginator


class AccountListView(RestrictedListView):
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
            qs = qs.filter(
                username__icontains=search) | qs.filter(
                first_name__icontains=search) | qs.filter(
                last_name__icontains=search)

        return qs

    def order_queryset(self, qs):
        qs = qs.order_by('first_name', 'last_name')
        return qs

    def get_paginate_by(self, queryset):
        # Overrides get_paginate_by to allow changing it in the template
        # as url param paginate_by=xx
        return self.request.GET.get('paginate_by', self.paginate_by)

    def setup(self, request, *args, **kwargs):
        org = get_object_or_404(Organization, slug=kwargs['org_slug'])
        kwargs['org'] = org
        if request.user.is_superuser or Administrator.objects.filter(
                user=request.user, client=org.client).exists():
            return super().setup(request, *args, **kwargs)
        else:
            raise Http404(
                "Organization not found."
                )


class AccountDetailView(LoginRequiredMixin, DetailView):
    model = Account
    template_name = "organizations/account_detail.html"
    context_object_name = "account"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["organization"] = self.kwargs['org']
        context["aliases"] = self.object.aliases.exclude(_alias_type=AliasType.REMEDIATOR)
        context["remediator_for_scanners"] = self.object.get_remediator_scanners()
        existing_pks = [scanner.get('pk') for scanner in context["remediator_for_scanners"]]
        context["scanners"] = list(Scanner.objects.filter(organization=self.kwargs['org'])
                                   .exclude(pk__in=existing_pks)
                                   .values('name', 'pk'))
        return context

    def setup(self, request, *args, **kwargs):
        org = get_object_or_404(Organization, slug=kwargs['org_slug'])
        kwargs['org'] = org
        if request.user.is_superuser or Administrator.objects.filter(
                user=request.user, client=org.client).exists():
            return super().setup(request, *args, **kwargs)
        else:
            raise Http404(
                "Organization not found."
                )

    def post(self, request, *args, **kwargs):
        trigger_name = request.headers.get('HX-Trigger-Name')

        match trigger_name:
            case 'remediator-check':
                acc = self.get_object()
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
                account_uuid = request.POST.get('account')
                org = self.kwargs.get('org')

                # Make sure the scanner and the account belong to the same organization
                if int(added_scanner_job_pk) not in \
                    [scanner.get('pk') for scanner in
                        Scanner.objects.filter(organization=org).values('pk')]:
                    raise Http404()

                Alias.objects.create(_alias_type=AliasType.REMEDIATOR,
                                     _value=added_scanner_job_pk,
                                     account_id=account_uuid)

            case 'rem-remediator':
                removed_scanner_job_pk = request.POST.get('rem-remediator')
                account_uuid = request.POST.get('account')

                Alias.objects.filter(_alias_type=AliasType.REMEDIATOR,
                                     _value=removed_scanner_job_pk,
                                     account_id=account_uuid).delete()

        return self.get(request, *args, **kwargs)
