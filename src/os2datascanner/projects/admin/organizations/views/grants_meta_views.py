from functools import reduce
from operator import or_, and_
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionDenied
from django.db.models import Prefetch, Q
from django.http import Http404
from django.shortcuts import redirect
from django.views import View

from os2datascanner.projects.admin.organizations.models import Organization
from os2datascanner.projects.grants.models import Grant, GraphGrant, SMBGrant, EWSGrant

from os2datascanner.projects.admin.adminapp.views.views import RestrictedListView
from os2datascanner.projects.grants.models.googleapigrant import GoogleApiGrant


class GrantListView(RestrictedListView):
    model = Organization
    template_name = "organizations/grants_list.html"
    context_object_name = "organizations"

    def get_queryset(self):
        user = self.request.user

        permissions = {
            'graphgrant': user.has_perm("grants.view_graphgrant"),
            'smbgrant': user.has_perm("grants.view_smbgrant"),
            'ewsgrant': user.has_perm("grants.view_ewsgrant"),
            'googleapigrant': user.has_perm("grants.view_googleapigrant"),
        }

        allowed_types = {key for key, allowed in permissions.items() if allowed}
        disallowed_types = {key for key, allowed in permissions.items() if not allowed}

        if not allowed_types:
            raise PermissionDenied

        # Build include (OR) clause for allowed types
        include_q = [Q(**{f"{grant_type}__isnull": False}) for grant_type in allowed_types]
        include_filter = reduce(or_, include_q)

        # Build exclude (AND) clause for disallowed types
        exclude_q = [Q(**{f"{grant_type}__isnull": True}) for grant_type in disallowed_types]
        exclude_filter = reduce(and_, exclude_q) if exclude_q else Q()

        # Final filter
        final_filter = include_filter & exclude_filter

        # Use in queryset
        grants = Grant.objects.select_subclasses().filter(final_filter)

        # Prefetch grants for each organization
        queryset = self.model.objects.prefetch_related(
            Prefetch('grant', queryset=grants, to_attr='prefetched_grants')
        )

        for org in queryset:
            # Annotate each organization with appropriate Grant list for user.
            org.grants = org.prefetched_grants

        return queryset


class GrantRedirectUpdateView(LoginRequiredMixin, View):
    """
    Redirects to different Grant-UpdateViews based on the object type.
    """

    def get(self, request, *args, **kwargs):
        grant_type = kwargs.get("type")
        grant_pk = kwargs.get("pk")

        match (grant_type, grant_pk):
            case (GraphGrant.__name__, grant_pk):
                return redirect("msgraphgrant-update", pk=grant_pk)

            case (SMBGrant.__name__, grant_pk):
                return redirect("smbgrant-update", pk=grant_pk)

            case (EWSGrant.__name__, grant_pk):
                return redirect("ewsgrant-update", pk=grant_pk)

            case (GoogleApiGrant.__name__, grant_pk):
                return redirect("googleapigrant-update", pk=grant_pk)

            case _:
                raise Http404
