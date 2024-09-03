from django.db.models import Q, Count, Prefetch

from ...adminapp.views.views import RestrictedListView
from ..models import OrganizationalUnit, Account, Position
from ...core.models import Feature
from ...adminapp.views.scanner_views import EmptyPagePaginator
from ..utils import ClientAdminMixin

from os2datascanner.core_organizational_structure.models.position import Role


class OrganizationalUnitListView(ClientAdminMixin, RestrictedListView):
    model = OrganizationalUnit
    template_name = 'organizations/orgunit_list.html'
    paginator_class = EmptyPagePaginator
    paginate_by = 10
    paginate_by_options = [10, 20, 50, 100, 250]

    # Filter queryset based on organization:
    def get_queryset(self):
        qs = super().get_queryset()

        org = self.kwargs['org']

        qs = qs.filter(organization=org)

        show_empty = self.request.GET.get("show_empty", "off") == "on"
        self.roles = self.request.GET.getlist("roles") or Role.values

        if show_empty:
            qs = qs.filter(Q(positions=None) | Q(positions__role__in=self.roles))
        else:
            qs = qs.filter(positions__role__in=self.roles).exclude(positions=None)

        if search_field := self.request.GET.get("search_field", ""):
            qs = qs.filter(Q(name__icontains=search_field) |
                           Q(parent__name__icontains=search_field))

        # Prefetch related manager and dpo accounts, as well as number of
        # associated accounts. Saves 3 queries per OU.
        qs = qs.prefetch_related(
                Prefetch(
                    'positions',
                    queryset=Position.managers.all().select_related('account'),
                    to_attr='managers'),
                Prefetch(
                    'positions',
                    queryset=Position.dpos.all().select_related('account'),
                    to_attr='dpos')
                ).annotate(
                    employee_count=Count('positions', filter=Q(positions__role=Role.EMPLOYEE)))

        # Prefetch parents to save one query per unit
        qs = qs.prefetch_related('parent')

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['organization'] = self.kwargs['org']
        context['FEATURES'] = Feature.__members__
        context['search_targets'] = [
            unit.uuid for unit in self.object_list] if self.request.GET.get(
            "search_field", None) else []
        context['show_empty'] = self.request.GET.get('show_empty', 'off') == 'on'
        context['paginate_by'] = int(self.request.GET.get('paginate_by', self.paginate_by))
        context['paginate_by_options'] = self.paginate_by_options
        context['roles'] = Role.choices
        context['checked_roles'] = self.roles
        return context

    def get_paginate_by(self, queryset):
        # Overrides get_paginate_by to allow changing it in the template
        # as url param paginate_by=xx
        return self.request.GET.get('paginate_by', self.paginate_by)

    def post(self, request, *args, **kwargs):

        if new_manager_uuid := request.POST.get("add-manager", None):
            orgunit = OrganizationalUnit.objects.get(pk=request.POST.get("orgunit"))
            new_manager = Account.objects.get(uuid=new_manager_uuid)
            Position.managers.get_or_create(account=new_manager, unit=orgunit)

        if rem_manager_uuid := request.POST.get("rem-manager", None):
            orgunit = OrganizationalUnit.objects.get(pk=request.POST.get("orgunit"))
            rem_manager = Account.objects.get(uuid=rem_manager_uuid)
            Position.managers.filter(account=rem_manager, unit=orgunit).delete()

        if new_dpo_uuid := request.POST.get("add-dpo", None):
            orgunit = OrganizationalUnit.objects.get(pk=request.POST.get("orgunit"))
            new_dpo = Account.objects.get(uuid=new_dpo_uuid)
            Position.dpos.get_or_create(account=new_dpo, unit=orgunit)

        if rem_dpo_uuid := request.POST.get("rem-dpo", None):
            orgunit = OrganizationalUnit.objects.get(pk=request.POST.get("orgunit"))
            rem_dpo = Account.objects.get(uuid=rem_dpo_uuid)
            Position.dpos.filter(account=rem_dpo, unit=orgunit).delete()

        response = self.get(request, *args, **kwargs)

        return response
