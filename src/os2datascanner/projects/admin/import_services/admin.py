# Part of the OSdatascanner system, copyright © 2014-2026 Magenta ApS.
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, you can
# obtain one at http://mozilla.org/MPL/2.0/.

from django.contrib import admin
from .models import (LDAPConfig, MSGraphConfiguration,
                     OS2moConfiguration, Realm,
                     KeycloakClient, IdentityProvider,
                     IdPMappers, AuthenticationFlow,
                     FlowExecution, GoogleWorkspaceConfig)


# Register your models here.

class ImportedAdmin(admin.ModelAdmin):
    readonly_fields = ('imported_id', 'last_import')


@admin.register(LDAPConfig)
class LDAPConfigAdmin(admin.ModelAdmin):
    """ Controls behaviour in Django Admin
               for the LDAPConfig model"""
    list_display = ('vendor', 'connection_url', 'connection_protocol',
                    'search_scope',
                    )


admin.site.register(MSGraphConfiguration)


admin.site.register(OS2moConfiguration)


@admin.register(Realm)
class RealmAdmin(admin.ModelAdmin):
    """ Controls behaviour in Django Admin
               for the Realm model"""
    list_display = ('realm_id', 'organization',)


admin.site.register(KeycloakClient)
admin.site.register(IdentityProvider)
admin.site.register(IdPMappers)
admin.site.register(AuthenticationFlow)
admin.site.register(FlowExecution)


@admin.register(GoogleWorkspaceConfig)
class GoogleWorkspaceConfigAdmin(admin.ModelAdmin):
    list_display = ("display_pk", "grant", "delegated_admin_email")
    fields = ("grant", "delegated_admin_email")

    def display_pk(self, obj):
        return str(obj.pk)

    display_pk.short_description = "PK"
