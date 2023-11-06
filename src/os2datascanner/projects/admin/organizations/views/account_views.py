from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import DetailView
from django.shortcuts import get_object_or_404
from django.http import Http404
from django.utils.translation import gettext_lazy as _

from ...core.models import Administrator
from ..models import Account, Organization, Alias
from ...adminapp.views.views import RestrictedListView
from ...adminapp.models.scannerjobs.scanner import Scanner


class AccountListView(RestrictedListView):
    model = Account
    template_name = "organizations/account_list.html"
    context_object_name = "accounts"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["organization"] = self.kwargs['org']
        return context

    def get_queryset(self):
        qs = super().get_queryset()

        org = self.kwargs['org']

        qs = qs.filter(organization=org)

        return qs

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
        context["aliases"] = self.object.aliases.exclude(_alias_type="remediator")
        context["remediator_for_scanners"] = self.object.get_remediator_scanners()
        existing_pks = [scanner.get('pk') for scanner in context["remediator_for_scanners"]]
        context["scanners"] = list(Scanner.objects.filter(organization=self.kwargs['org'])
                                   .exclude(pk__in=existing_pks)
                                   .values('name', 'pk'))
        if "0" not in existing_pks:
            context["scanners"].append({'pk': '0', 'name': _('All scanners')})
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
        added_scanner_job_pk = request.POST.get('add-remediator')
        removed_scanner_job_pk = request.POST.get('rem-remediator')
        account_uuid = request.POST.get('account')
        org = self.kwargs.get('org')

        if added_scanner_job_pk and account_uuid:
            if added_scanner_job_pk != "0" and \
                int(added_scanner_job_pk) not in \
                    [scanner.get('pk') for scanner in
                        Scanner.objects.filter(organization=org).values('pk')]:
                raise Http404()
            Alias.objects.create(_alias_type="remediator",
                                 _value=added_scanner_job_pk,
                                 account_id=account_uuid)
        elif removed_scanner_job_pk and account_uuid:
            Alias.objects.filter(_alias_type="remediator",
                                 _value=removed_scanner_job_pk,
                                 account_id=account_uuid).delete()

        return self.get(request, *args, **kwargs)
