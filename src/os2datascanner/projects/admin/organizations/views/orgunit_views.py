from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage
from django.http import Http404
from django.utils.translation import ugettext_lazy as _

from ...adminapp.views.views import RestrictedListView
from ..models import OrganizationalUnit, Organization, Account, Position
from ...core.models import Feature, Administrator


class EmptyPagePaginator(Paginator):
    def validate_number(self, number):
        try:
            return super(EmptyPagePaginator, self).validate_number(number)
        except EmptyPage:
            if number > 1:
                return self.num_pages
            else:
                raise Http404(_('The page does not exist'))


class OrganizationalUnitListView(RestrictedListView):
    model = OrganizationalUnit
    context_object_name = 'orgunit_list'
    template_name = 'organizations/orgunit_list.html'
    paginator = EmptyPagePaginator
    paginate_by = 10
    paginate_by_options = [10, 20, 50, 100]

    # Filter queryset based on organization:
    def get_queryset(self):
        base_qs = super().get_queryset()

        org = self.kwargs['org']

        parent_query = Q(parent__isnull=True, organization=org)

        is_htmx = self.request.headers.get("HX-Request", False)
        if is_htmx:
            htmx_trigger = self.request.headers.get("HX-Trigger-Name", None)
            if htmx_trigger == "children":
                parent_query = Q(parent__pk=self.request.GET.get("parent"), organization=org)

        if search_field := self.request.GET.get("search_field", ""):
            parent_query = Q(name__icontains=search_field, organization=org)

        units = base_qs.filter(parent_query)

        show_empty = self.request.GET.get("show_empty", "off") == "on"
        if not show_empty:
            units = units.exclude(positions=None)

        return units

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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['paginate_by'] = int(self.request.GET.get('paginate_by', self.paginate_by))
        context['paginate_by_options'] = self.paginate_by_options
        context['organization'] = self.kwargs['org']
        context['accounts'] = Account.objects.filter(organization=self.kwargs['org'])
        context['FEATURES'] = Feature.__members__
        context['search_targets'] = [
            unit.uuid for unit in self.object_list] if self.request.GET.get(
            "search_field", None) else []
        return context

    def get_paginate_by(self, queryset):
        # Overrides get_paginate_by to allow changing it in the template
        # as url param paginate_by=xx
        return self.request.GET.get('paginate_by', self.paginate_by)

    def post(self, request, *args, **kwargs):

        if new_manager_uuid := request.POST.get("add-manager", None):
            orgunit = OrganizationalUnit.objects.get(pk=request.POST.get("orgunit"))
            new_manager = Account.objects.get(uuid=new_manager_uuid)
            Position.objects.get_or_create(account=new_manager, unit=orgunit, role="manager")

        if rem_manager_uuid := request.POST.get("rem-manager", None):
            orgunit = OrganizationalUnit.objects.get(pk=request.POST.get("orgunit"))
            rem_manager = Account.objects.get(uuid=rem_manager_uuid)
            Position.objects.filter(account=rem_manager, unit=orgunit, role="manager").delete()

        response = self.get(request, *args, **kwargs)

        return response
