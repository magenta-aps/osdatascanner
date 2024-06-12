from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from .models import EWSGrant, SMBGrant, GraphGrant


@admin.register(EWSGrant)
class EWSGrantAdmin(admin.ModelAdmin):
    fields = ["organization", "username", "password"]
    readonly_fields = ["password"]

    @admin.display(description=_("password"))
    def password(self, obj):
        return format_html(
                "<em>{}</em>",
                _("defined") if obj._password else _("not defined"))


@admin.register(SMBGrant)
class SMBGrantAdmin(admin.ModelAdmin):
    fields = ["organization", "domain", "username", "password"]
    readonly_fields = ["password"]

    @admin.display(description=_("password"))
    def password(self, obj):
        return format_html(
                "<em>{}</em>",
                _("defined") if obj._password else _("not defined"))


@admin.register(GraphGrant)
class GraphGrantAdmin(admin.ModelAdmin):
    fields = ["organization", "app_id", "tenant_id", "client_secret"]
    readonly_fields = ["client_secret"]

    @admin.display(description=_("client secret"))
    def client_secret(self, obj):
        return format_html(
                "<em>{}</em>",
                _("defined") if obj._client_secret else _("not defined"))
