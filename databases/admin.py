from django.contrib import admin
from core.admin import admin_site
from .models import ExternalDatabase


class ExternalDatabaseAdmin(admin.ModelAdmin):
    list_display = ('agency', 'db_type', 'country',)
    list_filter = ('db_type', 'paid', 'government_db', 'country',)


admin_site.register(ExternalDatabase, ExternalDatabaseAdmin)
