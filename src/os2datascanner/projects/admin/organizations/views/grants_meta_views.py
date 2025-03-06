from itertools import chain
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Prefetch
from django.http import Http404
from django.shortcuts import redirect
from django.views import View


from os2datascanner.projects.admin.organizations.models import Organization
from os2datascanner.projects.grants.models import GraphGrant, SMBGrant, EWSGrant

from os2datascanner.projects.admin.adminapp.views.views import RestrictedListView


class GrantListView(RestrictedListView):
    model = Organization
    template_name = "organizations/grants_list.html"
    context_object_name = "organizations"

    def get_queryset(self):
        queryset = self.model.objects.prefetch_related(
            Prefetch('graphgrant', to_attr='prefetched_graph_grants'),
            Prefetch('smbgrant', to_attr='prefetched_smb_grants'),
            Prefetch('ewsgrant', to_attr='prefetched_ews_grants')
        )

        for org in queryset:
            # Combine the related objects into a single attribute
            org.grants = list(chain(
                org.prefetched_graph_grants,
                org.prefetched_smb_grants,
                org.prefetched_ews_grants
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

            case _:
                raise Http404
