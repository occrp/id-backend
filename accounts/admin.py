from django.contrib import admin
from core.admin import admin_site
from .models import Network, Profile


class NetworkAdmin(admin.ModelAdmin):
    list_display = ('short_name', 'long_name',)


class ProfileAdmin(admin.ModelAdmin):
    list_display = ('email', 'first_name', 'last_name',
                    'organization', 'network')
    search_fields = ('email', 'first_name', 'last_name')
    fields = ('email', 'first_name', 'last_name', 'organization',
              'phone_number', 'network', 'country',
              'is_superuser', 'is_staff', 'is_active')
    exclude = ('password', 'last_login', 'groups',
               'user_permissions', 'date_joined',)


admin_site.register(Network, NetworkAdmin)
admin_site.register(Profile, ProfileAdmin)
