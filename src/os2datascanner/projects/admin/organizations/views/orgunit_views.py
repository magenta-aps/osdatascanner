from django.db.models import Q, Count, Prefetch
from django.contrib.auth.mixins import PermissionRequiredMixin

from ...adminapp.views.views import RestrictedListView
from ..models import (OrganizationalUnit, Account, Position,
                      Organization, OrganizationalUnitSerializer)
from ...core.models import Feature
from ...adminapp.views.scanner_views import EmptyPagePaginator
from ..utils import ClientAdminMixin
from os2datascanner.core_organizational_structure.models.position import Role
from django.shortcuts import get_object_or_404
from ..publish import publish_events
from ..broadcast_bulk_events import BulkUpdateEvent


class OrganizationalUnitListView(ClientAdminMixin, PermissionRequiredMixin, RestrictedListView):
    model = OrganizationalUnit
    template_name = 'organizations/orgunit_list.html'
    permission_required = 'organizations.view_organizationalunit'
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
        context['show_empty'] = self.request.GET.get('show_empty', 'off') == 'on'
        context['show_hidden'] = self.request.GET.get('show_hidden', 'off') == 'on'
        context['paginate_by'] = int(self.request.GET.get('paginate_by', self.paginate_by))
        context['paginate_by_options'] = self.paginate_by_options
        context['roles'] = Role.choices
        context['checked_roles'] = self.roles

        return context

    def get_paginate_by(self, queryset):
        # Allow `paginate_by` to be dynamically updated via URL params
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


class OrganizationalUnitEditVisibility(ClientAdminMixin, PermissionRequiredMixin,
                                       RestrictedListView):
    model = OrganizationalUnit
    template_name = 'organizations/edit_hidden_state_page.html'
    permission_required = 'organizations.change_visibility_organizationalunit'
    paginator_class = EmptyPagePaginator
    paginate_by = 60
    paginate_by_options = [60, 120, 240, 480]

    def get_queryset(self):
        qs = super().get_queryset()
        org_slug = self.kwargs['org_slug']
        qs = qs.filter(organization__slug=org_slug)

        if search_field := self.request.GET.get('search_field', ''):
            qs = qs.filter(Q(name__icontains=search_field))

        qs = qs.order_by('name')
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        org_slug = self.kwargs['org_slug']
        organization = get_object_or_404(Organization, slug=org_slug)

        context['organization'] = organization
        context['FEATURES'] = Feature.__members__
        context['paginate_by'] = int(self.request.GET.get('paginate_by', self.paginate_by))
        context['paginate_by_options'] = self.paginate_by_options

        return context

    def get_paginate_by(self, queryset):
        # Allow `paginate_by` to be dynamically updated via URL params
        return self.request.GET.get('paginate_by', self.paginate_by)

    def update_hidden_state_for_org_unit(self, queryset):
        update_dict = {"OrganizationalUnit": OrganizationalUnitSerializer(
            queryset.all(), many=True).data}
        publish_events([BulkUpdateEvent(update_dict)])

    def post(self, request, *args, **kwargs):
        is_htmx = self.request.headers.get("HX-Request", False) == "true"
        htmx_trigger = self.request.headers.get('HX-Trigger-Name')

        # Fetch the authorized queryset for the org
        self.object_list = self.get_queryset()

        if is_htmx:
            # Toggle hidden status for a single OU
            if htmx_trigger == "toggle_orgunit_hidden_state":
                org_unit_pk = self.request.POST.get("pk")
                org_unit = self.object_list.filter(pk=org_unit_pk)
                # This is a whack but functioning way to change the hidden state to the opposite
                org_unit.update(hidden=Q(hidden=False))
                self.update_hidden_state_for_org_unit(org_unit)

            # Change all OUs to visible
            elif htmx_trigger == "unhide_all_orgunits":
                self.object_list.update(hidden=False)
                self.update_hidden_state_for_org_unit(self.object_list)

            # Change all OUs to hidden
            elif htmx_trigger == "hide_all_orgunits":
                self.object_list.update(hidden=True)
                self.update_hidden_state_for_org_unit(self.object_list)

        context = self.get_context_data()
        return self.render_to_response(context)
