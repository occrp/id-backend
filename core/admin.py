from django.contrib.admin import AdminSite

from oauth2_provider.models import AccessToken

admin_site = AdminSite()
admin_site.site_header = 'ID Administration'
