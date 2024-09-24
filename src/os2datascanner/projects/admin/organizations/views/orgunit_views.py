from django.db.models import Q, Count, Prefetch
from ...adminapp.views.views import RestrictedListView
from ..models import OrganizationalUnit, Account, Position, Organization
from ...core.models import Feature
from ...adminapp.views.scanner_views import EmptyPagePaginator
from ..utils import ClientAdminMixin
from os2datascanner.core_organizational_structure.models.position import Role
from django.shortcuts import get_object_or_404, render


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
        show_hidden = self.request.GET.get("show_hidden", "off") == "on"
        self.roles = self.request.GET.getlist("roles") or Role.values

        if show_empty:
            qs = qs.filter(Q(positions=None) | Q(positions__role__in=self.roles))
        else:
            qs = qs.filter(positions__role__in=self.roles).exclude(positions=None)

        if search_field := self.request.GET.get("search_field", ""):
            qs = qs.filter(Q(name__icontains=search_field) |
                           Q(parent__name__icontains=search_field))

        # Exclude hidden units by default
        if not show_hidden:
            qs = qs.filter(hidden=False)

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
        context['uni_dpos'] = Account.objects.filter(
            organization=self.kwargs['org'],
            is_universal_dpo=True
        )
        context['search_targets'] = [
            unit.uuid for unit in self.object_list] if self.request.GET.get(
            "search_field", None) else []
        context['show_empty'] = self.request.GET.get('show_empty', 'off') == 'on'
        context['show_hidden'] = self.request.GET.get('show_hidden', 'off') == 'on'
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
        # Add manager
        if new_manager_uuid := request.POST.get("add-manager", None):
            orgunit = OrganizationalUnit.objects.get(pk=request.POST.get("orgunit"))
            new_manager = Account.objects.get(uuid=new_manager_uuid)
            Position.managers.get_or_create(account=new_manager, unit=orgunit)

        # Remove manager
        if rem_manager_uuid := request.POST.get("rem-manager", None):
            orgunit = OrganizationalUnit.objects.get(pk=request.POST.get("orgunit"))
            rem_manager = Account.objects.get(uuid=rem_manager_uuid)
            Position.managers.filter(account=rem_manager, unit=orgunit).delete()

        # Add DPO
        if new_dpo_uuid := request.POST.get("add-dpo", None):
            orgunit = OrganizationalUnit.objects.get(pk=request.POST.get("orgunit"))
            new_dpo = Account.objects.get(uuid=new_dpo_uuid)
            Position.dpos.get_or_create(account=new_dpo, unit=orgunit)

        # Remove DPO
        if rem_dpo_uuid := request.POST.get("rem-dpo", None):
            orgunit = OrganizationalUnit.objects.get(pk=request.POST.get("orgunit"))
            rem_dpo = Account.objects.get(uuid=rem_dpo_uuid)
            Position.dpos.filter(account=rem_dpo, unit=orgunit).delete()

        # Add universal DPO
        if new_uni_dpo_uuid := request.POST.get("add-uni-dpo", None):
            new_uni_dpo = Account.objects.get(uuid=new_uni_dpo_uuid)
            new_uni_dpo.is_universal_dpo = True
            new_uni_dpo.save()

        # Remove universal DPO
        if rem_uni_dpo_uuid := request.POST.get("rem-uni-dpo", None):
            rem_uni_dpo = Account.objects.get(uuid=rem_uni_dpo_uuid)
            rem_uni_dpo.is_universal_dpo = False
            rem_uni_dpo.save()

        response = self.get(request, *args, **kwargs)

        return response


class OrganizationalUnitEditVisibility(ClientAdminMixin, RestrictedListView):
    model = OrganizationalUnit
    template_name = 'organizations/edit_visibility_page.html'
    paginator_class = EmptyPagePaginator
    paginate_by = 60
    paginate_by_options = [60, 120, 240, 480]

    def get_queryset(self):
        qs = super().get_queryset()
        org_slug = self.kwargs['org_slug']
        qs = qs.filter(organization__slug=org_slug)

        search_field = self.request.GET.get('search_field', '')
        if search_field:
            qs = qs.filter(Q(name__icontains=search_field))

        qs = qs.order_by('name')
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        org_slug = self.kwargs['org_slug']
        organization = get_object_or_404(Organization, slug=org_slug)
        context['organization'] = organization
        context['FEATURES'] = Feature.__members__
        context['search_field'] = self.request.GET.get('search_field', '')
        context['search_targets'] = [unit.uuid for unit in self.object_list]
        context['show_empty'] = self.request.GET.get('show_empty', 'off') == 'on'
        context['paginate_by'] = int(self.request.GET.get('paginate_by', self.paginate_by))
        context['paginate_by_options'] = self.paginate_by_options
        return context

    def get_paginate_by(self, queryset):
        paginate_by = self.request.GET.get('paginate_by') or self.request.POST.get('paginate_by')
        if paginate_by:
            self.request.session['paginate_by'] = int(paginate_by)
        else:
            paginate_by = self.request.session.get('paginate_by', self.paginate_by)
        return int(paginate_by)

    def post(self, request, *args, **kwargs):
        org_slug = self.kwargs['org_slug']

        # Toggle visibility for a single orgunit
        if orgunit_pk := request.POST.get("toggle_visibility"):
            orgunit = get_object_or_404(
                OrganizationalUnit, pk=orgunit_pk, organization__slug=org_slug)
            orgunit.hidden = not orgunit.hidden
            orgunit.save()

        # Set visibility for all orgunits
        elif 'set_all_visibility' in request.POST:
            visibility = request.POST.get('visibility')
            hidden = visibility != 'true'
            organization = get_object_or_404(Organization, slug=org_slug)
            OrganizationalUnit.objects.filter(organization=organization).update(hidden=hidden)

        self.object_list = self.get_queryset()
        context = self.get_context_data()

        if request.headers.get("HX-Request"):
            return render(request, 'organizations/edit_visibility_orgunit_list.html', context)
        else:
            return render(request, 'organizations/edit_visibility_page.html', context)
