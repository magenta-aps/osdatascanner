from itertools import chain
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionDenied
from django.db.models import Prefetch
from django.http import Http404
from django.shortcuts import redirect
from django.views import View


from os2datascanner.projects.admin.organizations.models import Organization
from os2datascanner.projects.grants.models import GraphGrant, SMBGrant, EWSGrant

from os2datascanner.projects.admin.adminapp.views.views import RestrictedListView
from os2datascanner.projects.grants.models.googleapigrant import GoogleApiGrant


class GrantListView(RestrictedListView):
    model = Organization
    template_name = "organizations/grants_list.html"
    context_object_name = "organizations"

    def get_queryset(self):
        gg_perm = self.request.user.has_perm("grants.view_graphgrant")
        sg_perm = self.request.user.has_perm("grants.view_smbgrant")
        eg_perm = self.request.user.has_perm("grants.view_ewsgrant")
        gag_perm = self.request.user.has_perm("grants.view_googleapigrant")

        if not (gg_perm or sg_perm or eg_perm):
            raise PermissionDenied

        prefetches = [
            Prefetch('graphgrant', to_attr='prefetched_graph_grants') if gg_perm else None,
            Prefetch('smbgrant', to_attr='prefetched_smb_grants') if sg_perm else None,
            Prefetch('ewsgrant', to_attr='prefetched_ews_grants') if eg_perm else None,
            Prefetch('googleapigrant', to_attr='prefetched_googleapi_grants') if gag_perm else None
        ]

        queryset = self.model.objects.prefetch_related(
            *[prefetch for prefetch in prefetches if prefetch is not None])

        for org in queryset:
            # Combine the related objects into a single attribute

            org.grants = list(chain(
                org.prefetched_graph_grants if gg_perm else [],
                org.prefetched_smb_grants if sg_perm else [],
                org.prefetched_ews_grants if eg_perm else [],
                org.prefetched_googleapi_grants if gag_perm else []
            ))

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
