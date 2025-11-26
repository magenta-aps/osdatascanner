import json

from django.http import HttpResponseRedirect
from django.urls import path, reverse
from django.utils.translation import gettext_lazy as _
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.template.response import TemplateResponse

from .models.documentreport import DocumentReport
from .models.scanner_reference import ScannerReference

from os2datascanner.engine2.pipeline import messages  # noqa
from os2datascanner.projects.report.organizations.models import Organization, Account
from os2datascanner.projects.report.reportapp.management.commands import (
        result_collector as r_c)

import os2datascanner.engine2.model._staging.sbsysdb  # noqa


@admin.register(DocumentReport)
class DocumentReportAdmin(admin.ModelAdmin):
    def get_urls(self):
        return [
            path("import/",
                 self.admin_site.admin_view(self.import_view),
                 name="os2datascanner_report_documentreport_import"),
        ] + super().get_urls()

    def import_view(self, request):
        match request.method:
            case "GET":
                return TemplateResponse(
                        request,
                        "admin/documentreport_import.html",
                        context={"orgs": Organization.objects.all()})
            case "POST":
                organization = None
                if org_pk := request.POST["org"]:
                    organization = Organization.objects.get(pk=org_pk)

                chunk = ""
                payloads = []
                for line in request.POST["json"].splitlines():
                    chunk += line
                    try:
                        payload = json.loads(chunk)
                        chunk = ""
                    except json.JSONDecodeError:
                        continue

                    if isinstance(payload, dict):
                        payloads.append(payload)
                    elif isinstance(payload, list):
                        payloads.extend(payload)

                for blob in payloads:
                    scan_tag, _ignored = r_c._identify_message(blob)
                    if scan_tag and organization:
                        scan_tag["organisation"] = {
                            "uuid": str(organization.uuid),
                            "name": organization.name
                        }

                    list(r_c.result_message_received_raw(blob))

                self.message_user(
                        request,
                        _("{count} JSON messages imported.").format(count=len(payloads)))
                return HttpResponseRedirect(
                        reverse("admin:os2datascanner_report_documentreport"
                                "_changelist"))

    list_display = (
        'presentation',
        'number_of_matches',
        'scanner_job',
        'aliases',
        'resolution_status',
        'resolution_time',
        'only_notify_superadmin',
    )

    list_filter = (
        'scanner_job',
    )

    def aliases(self, dr):
        return ", ".join([alias_relation.account.username
                          for alias_relation in dr.alias_relations.all()])

    def get_queryset(self, request):
        return super(DocumentReportAdmin, self).get_queryset(request).prefetch_related(
            'alias_relations')


@admin.register(ScannerReference)
class ScannerReferenceAdmin(admin.ModelAdmin):
    list_display = (
        "scanner_name",
        "scanner_pk",
        "organization",
    )

    list_filter = (
        "organization",
    )


class ProfileInline(admin.TabularInline):

    """Inline class for user accounts."""

    model = Account
    extra = 1
    can_delete = False

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        field = super().formfield_for_foreignkey(db_field, request, **kwargs)

        if db_field.name == 'organization':
            if not request.user.is_superuser:
                field.queryset = Organization.objects.filter(
                    name=request.user.account.organization.name
                )
                field.empty_label = None

        return field


class MyUserAdmin(UserAdmin):

    """Custom user admin class."""

    inlines = [ProfileInline]
    can_delete = False

    def get_form(self, request, obj=None, **kwargs):
        if not request.user.is_superuser:
            self.fieldsets = (
                (None,
                 {'fields': ('username', 'password', 'is_active')}),
                (_('Personal info'),  # noqa: F821
                 {'fields': ('first_name', 'last_name', 'email')}),
                (_('Important dates'), {'fields': ('last_login',  # noqa: F821
                                                   'date_joined')}),
            )

            self.exclude = ['is_superuser', 'permissions', 'groups']
        return super().get_form(request, obj, **kwargs)

    def get_queryset(self, request):
        """Only allow users belonging to same organization to be edited."""

        qs = super().get_queryset(request)

        if request.user.is_superuser:
            return qs
        return qs.filter(
            account__organization=request.user.account.organization
        )


admin.site.unregister(User)
admin.site.register(User, MyUserAdmin)
