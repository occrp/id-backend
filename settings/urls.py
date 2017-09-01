from django.conf import settings
from django.conf.urls import include, url
from django.views.generic import TemplateView
from django.views.generic.base import RedirectView
from django.views.i18n import javascript_catalog
from django.conf.urls.static import static

from core.manage import Panel
from core.admin import admin_site
from accounts.manage import Statistics
from core.auth import perm
from core.views import home, tickets_home

# Instead of admin auto-discovery:
from databases.admin import ExternalDatabaseAdmin  # noqa
from accounts.admin import ProfileAdmin  # noqa
from ticket.admin import BudgetAdmin  # noqa

js_info_dict = {
    'packages': ('ticket'),
}

urlpatterns = [
    url(r'^$', home, name='home'),
    url(r'^tickets', tickets_home, name='tickets_home'),
    url(r'^about/id2/$', perm('any', TemplateView, template_name="about_id.jinja"), name='about_id'),
    url(r'^about/occrp/$', perm('any', TemplateView, template_name="about_us.jinja"), name='about_us'),
    url(r'^o/', include('oauth2_provider.urls', namespace='oauth2_provider')),

    url(r'^admin/', admin_site.urls),
    url(r'^manage/$', perm('staff', Panel), name='manage_panel'),
    url(r'^statistics/$', perm('admin', Statistics), name='statistics'),

    url(r'^accounts/', include('accounts.urls')),

    url(r'^ticket/', RedirectView.as_view(
        url='/tickets/', permanent=True), name='old_ticket_redirect'),
    url(r'^databases/', include('databases.urls')),

    # url(r'^i18n/', include('django.conf.urls.i18n')),
    url(r'^jsi18n/$', javascript_catalog, js_info_dict),
    url(r'^jsi18n/(?P<packages>\S+?)/$', javascript_catalog),

    url(r'^captcha/', include('captcha.urls')),

    # API V3
    url(r'^api/v3/', include('api_v3.urls')),

] + (
    static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
)


handler403 = 'core.errors.redirect_403'
