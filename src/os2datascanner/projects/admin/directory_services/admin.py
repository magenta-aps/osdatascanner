from django.contrib import admin

from .models import LDAPConfig

# Register your models here.

for model in [LDAPConfig]:
    admin.site.register(model)
