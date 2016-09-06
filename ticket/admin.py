from django.contrib import admin
from core.admin import admin_site
from .models import Budget


class BudgetAdmin(admin.ModelAdmin):
    list_display = ('name', 'description',)


admin_site.register(Budget, BudgetAdmin)
