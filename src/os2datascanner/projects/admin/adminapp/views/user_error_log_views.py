import structlog

from django.core.exceptions import PermissionDenied
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.utils.translation import gettext_lazy as _

from os2datascanner.projects.utils.pagination import EmptyPagePaginator

from .views import RestrictedListView
from ..models.usererrorlog import UserErrorLog
from ....utils.view_mixins import CSVExportMixin

logger = structlog.get_logger("adminapp")


def count_new_errors(user) -> int:
    """Return the number of new user error logs available to the user."""
    usererrorlog = None
    if user.has_perm("core.view_client"):
        usererrorlog = UserErrorLog.objects.all()
    else:
        user_orgs = user.administrator_for.client.organizations.all()
        usererrorlog = UserErrorLog.objects.filter(organization__in=user_orgs)
    return usererrorlog.filter(is_new=True).count()


class UserErrorLogView(PermissionRequiredMixin, RestrictedListView):
    """Displays list of errors encountered."""
    permission_required = 'os2datascanner.view_usererrorlog'
    template_name = 'error_log.html'
    model = UserErrorLog
    paginate_by = 10
    paginator_class = EmptyPagePaginator
    paginate_by_options = [10, 20, 50, 100, 250]

    def get_queryset(self):
        """Order errors by most recent scan."""
        qs = super().get_queryset().filter(is_resolved=False)

        qs = self.sort_queryset(qs)

        # We often use the error_logs scan_status and scanner as well. Prefetch that!
        qs = qs.prefetch_related("scan_status__scanner")

        return qs

    def sort_queryset(self, qs):
        allowed_sorting_properties = {'error_message', 'path', 'scan_status', 'pk'}

        if (sort_key := self.request.GET.get('order_by')) and (
                order := self.request.GET.get('order')):

            if sort_key not in allowed_sorting_properties:
                logger.warning(
                        "UserErrorLogView:"
                        f" ignoring unsupported sort key {sort_key}")
                return qs.order_by('-pk')

            if order != "ascending":
                sort_key = '-' + sort_key

            qs = qs.order_by(sort_key, 'pk')
        else:
            qs = qs.order_by('-pk')

        if search := self.request.GET.get('search_field'):
            qs = qs.filter(path__icontains=search) | qs.filter(error_message__icontains=search)

        if self.request.GET.get('show_seen', 'off') != 'on':
            qs = qs.filter(is_new=True)

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['paginate_by'] = int(self.request.GET.get('paginate_by', self.paginate_by))
        context['paginate_by_options'] = self.paginate_by_options

        context['order_by'] = self.request.GET.get('order_by', 'pk')
        context['order'] = self.request.GET.get('order', 'descending')

        context['show_seen'] = self.request.GET.get('show_seen', 'off') == 'on'

        context["new_error_logs"] = count_new_errors(self.request.user)

        return context

    def get_paginate_by(self, queryset):
        # Overrides get_paginate_by to allow changing it in the template
        # as url param paginate_by=xx
        return self.request.GET.get('paginate_by', self.paginate_by)

    def post(self, request, *args, **kwargs):
        is_htmx = self.request.headers.get("HX-Request", False) == "true"
        htmx_trigger = self.request.headers.get('HX-Trigger-Name')

        self.object_list = self.get_queryset()

        if is_htmx:
            # Only allow removal of errors if the user has the correct permissions
            if htmx_trigger in ("remove_errorlog", "remove_selected", "remove_all") \
                    and not self.request.user.has_perm('os2datascanner.resolve_usererrorlog'):
                raise PermissionDenied()
            elif htmx_trigger in ("see_errorlog", "see_all") \
                    and not self.request.user.has_perm('os2datascanner.mark_view_usererrorlog'):
                raise PermissionDenied()

            if htmx_trigger == "remove_errorlog":
                delete_pk = self.request.POST.get('pk')
                self.object_list.filter(pk=delete_pk).update(is_resolved=True, is_new=False)
            elif htmx_trigger == "remove_selected":
                self.object_list.filter(pk__in=self.request.POST.getlist(
                    'table-checkbox')).update(is_resolved=True, is_new=False)
            elif htmx_trigger == "remove_all":
                self.object_list.update(is_resolved=True, is_new=False)
            elif htmx_trigger == "see_errorlog":
                seen_pk = self.request.POST.get('pk')
                self.object_list.filter(pk=seen_pk).update(is_new=False)
            elif htmx_trigger == "see_all":
                self.object_list.update(is_new=False)

        context = self.get_context_data()

        return self.render_to_response(context)


class UserErrorLogCSVView(CSVExportMixin, UserErrorLogView):
    permission_required = "os2datascanner.export_usererrorlog"
    columns = [
        {
            'name': 'scan_status__scan_tag__time',
            'label': _("Scan time"),
            'type': CSVExportMixin.ColumnType.FIELD,
        },
        {
            'name': 'path',
            'label': _("Path"),
            'type': CSVExportMixin.ColumnType.FIELD,
        },
        {
            'name': 'scan_status__scanner__name',
            'label': _("Scanner job"),
            'type': CSVExportMixin.ColumnType.FIELD,
        },
        {
            'name': 'error_message',
            'label': _("Error message"),
            'type': CSVExportMixin.ColumnType.FIELD,
        },
    ]
    exported_filename = 'os2datascanner_usererrorlogs'

    def sort_queryset(self, qs):
        # Override the sorting method to make sure we get both seen and unseen
        # UserErrorLog-objects.
        return qs
