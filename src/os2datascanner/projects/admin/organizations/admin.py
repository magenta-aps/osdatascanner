from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from os2datascanner.projects.admin.import_services.admin import ImportedAdmin

from .models import Organization, OrganizationalUnit, Account, Position, Alias

# Register your models here.

for model in [OrganizationalUnit, Position]:
    admin.site.register(model, ImportedAdmin)


@admin.register(Alias)
class AliasAdmin(ImportedAdmin):
    """ Controls behaviour in Django Admin
           for the Alias model"""
    list_filter = ["_alias_type"]
    fields = ('account', '_alias_type', '_value',
              'last_import_requested', 'last_import'
              )
    list_display = ('account', '_alias_type', '_value', 'last_import')


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    """ Controls behaviour in Django Admin
         for the Organization model"""

    fieldsets = [
        (
            None,
            {
                "fields": ('name', 'slug', 'client', 'contact_email',
                           'contact_phone', 'email_notification_schedule',
                           'outlook_categorize_email_permission',
                           'outlook_delete_email_permission', 'onedrive_delete_permission',
                           'email_header_banner')
            },
        ),
        (
            _("Tab access"),
            {
                "fields": ('leadertab_access', 'dpotab_access')
            },
        ),
        (
            _("Support button settings"),
            {
                "fields": ('show_support_button', 'support_contact_method',
                           'support_name', 'support_value', 'dpo_contact_method',
                           'dpo_name', 'dpo_value')
            }
        )
    ]
    list_display = ('name', 'client', 'contact_email', 'contact_phone',)
    search_fields = ('name', 'client__name')


@admin.register(Account)
class AccountAdmin(ImportedAdmin):
    """ Controls behaviour in Django Admin
     for the Account model"""

    # TODO: Consider if 'units' is needed here?
    #  At the time of writing units does not work
    fields = ('username', 'first_name', 'last_name', 'email',
              'organization', 'manager', 'imported_id', 'last_import',
              'is_superuser',
              )
    list_display = ('username', 'first_name', 'last_name', 'email',
                    'organization', 'last_import',
                    )
    search_fields = ('username', 'first_name', 'last_name', 'email',
                     'organization__name',
                     )
    list_filter = (
        'organization',
    )
