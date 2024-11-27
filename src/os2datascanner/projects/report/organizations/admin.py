# Register your models here.
from django.contrib import admin


from .models.account import Account
from .models.account_outlook_setting import AccountOutlookSetting, OutlookCategory
from .models.aliases import Alias
from .models.organization import Organization
from .models.organizational_unit import OrganizationalUnit
from .models.position import Position


class ReadOnlyAdminMixin:
    """ Defines that model is read only through django admin interface
        Useful here because objects are owned by another system (admin)
        We can't change instances directly - only view"""

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Alias)
class AliasAdmin(ReadOnlyAdminMixin, admin.ModelAdmin):
    list_filter = ["_alias_type"]
    list_display = ('user', 'account', '_alias_type', '_value', 'shared')
    readonly_fields = ('user', 'account', '_alias_type', '_value', 'shared')


@admin.register(Account)
class AccountAdmin(ReadOnlyAdminMixin, admin.ModelAdmin):
    list_display = (
        'username',
        'first_name',
        'last_name',
        'email',
        'organization',
        'manager',
        'uuid',)
    readonly_fields = (
        'username',
        'first_name',
        'last_name',
        'email',
        'organization',
        'manager',
        'uuid',)


@admin.register(AccountOutlookSetting)
class AccountOutlookSettingAdmin(ReadOnlyAdminMixin, admin.ModelAdmin):
    list_display = ['account', 'categorize_email']


@admin.register(OutlookCategory)
class OutlookCategoryAdmin(ReadOnlyAdminMixin, admin.ModelAdmin):
    list_display = ['account_outlook_setting', 'name', 'category_name', 'category_colour']


@admin.register(Organization)
class OrganizationAdmin(ReadOnlyAdminMixin, admin.ModelAdmin):
    list_display = ('name', 'uuid',)
    readonly_fields = ('name', 'uuid',)


@admin.register(OrganizationalUnit)
class OrganizationalUnitAdmin(ReadOnlyAdminMixin, admin.ModelAdmin):
    list_display = ('name', 'hidden', 'parent', 'organization', 'uuid')
    readonly_fields = ('name', 'hidden', 'parent', 'organization', 'uuid')


@admin.register(Position)
class PositionAdmin(ReadOnlyAdminMixin, admin.ModelAdmin):
    list_display = ('account', 'unit', 'role')
    readonly_fields = ('account', 'unit', 'role')
