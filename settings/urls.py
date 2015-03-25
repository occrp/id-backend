from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView

from id import databases, requests, search, accounts
from id import validation, admin, tasks, errors
from core.auth import perm

import ticket.validators
import ticket.views

from django.contrib.auth import views as auth_views
from registration.views import RegistrationView
from registration.views import ActivationView

js_info_dict = {
    'packages': ('id', 'ticket', 'search', 'podaci'),
}

urlpatterns = patterns('',
    url(r'^$',                              perm('any', TemplateView, template_name="splash.jinja"), name="home"),
    url(r'^about/$',                        perm('any', TemplateView, template_name="about_us.jinja"), name='about_us'),

    url(r'^admin/$',                        perm('staff', admin.Panel), name='admin_panel'),
    url(r'^admin/scrapers/request/$',       perm('staff', admin.DatabaseScrapeRequestCreate), name='admin_scrapers_request'),

    url(r'^admin/storage/$',                perm('admin', admin.Storage), name='admin_storage'),
    url(r'^admin/statistics/$',             perm('admin', admin.Statistics), name='statistics'),

    url(r'^search/$',                       perm('any', search.CombinedSearchHandler), name="search"),
    url(r'^search/entities/$',              perm('any', search.CombinedSearchHandler), name='search_entities'), # still needed for ajax only

    #url(r'^request/$', requests.RequestListHandler.as_view(), name='request_list'),
    #url(r'^request/(?P<ticket_id>[0-9]+)/details/$', requests.RequestDetailsHandler.as_view(), name='request_details'),
    #url(r'^request/(?P<ticket_id>[0-9]+)/cancel/$', requests.RequestCancelHandler.as_view(), name='request_cancel'),
    url(r'^request/(?P<ticket_id>[0-9]+)/reopen/$', requests.RequestReopenHandler.as_view(), name='request_reopen'),
    url(r'^request/(?P<ticket_id>[0-9]+)/pay/$', requests.RequestPaidHandler.as_view(), name='request_mark_paid'),
    url(r'^request/(?P<ticket_id>[0-9]+)/charge/$', requests.RequestAddChargeHandler.as_view(), name='request_charge_add'),
    url(r'^request/(?P<ticket_id>[0-9]+)/leave/$', requests.RequestLeaveHandler.as_view(), name='ticket_leave'),
    #url(r'^request/submit/$', requests.RequestHandler.as_view(), name='request'),
    url(r'^request/request_unauthorized/$', requests.RequestUnauthorized.as_view(), name='request_unauthorized'),
    url(r'^request/respond/$', requests.ResponseListHandler.as_view(), name='response_list'),
    url(r'^request/public/$', requests.PublicListHandler.as_view(), name='public_list'),
    url(r'^request/manage/unassigned/$', requests.AdminUnassignedTicketsHandler.as_view(), name='ticket_admin_unassigned'),
    url(r'^request/manage/deadline/$', requests.AdminDeadlineTicketsHandler.as_view(), name='ticket_admin_deadline'),
    url(r'^request/manage/history/$', requests.AdminHistoryTicketsHandler.as_view(), name='ticket_admin_history'),
    url(r'^request/manage/flagged/$', requests.AdminFlaggedTicketsHandler.as_view(), name='ticket_admin_flagged'),
    #url(r'^request/manage/(?P<ticket_id>[0-9]+)/edit/$', requests.RequestHandler.as_view(), name='ticket_edit'),
    #url(r'^request/manage/(?P<ticket_id>[0-9]+)/settings/$', requests.AdminSettingsHandler.as_view(), name='ticket_admin_settings'),
    url(r'^request/charges/customer/$', requests.AdminCustomerChargesHandler.as_view(), name='ticket_admin_customer_charges'),
    url(r'^request/charges/(?P<charge_key>.+)/reconcile/$', requests.AdminChargeReconcileInlineHandler.as_view(), name='ticket_admin_reconcile_charges'),
    url(r'^request/charges/outstanding/$', requests.AdminOutstandingChargesHandler.as_view(), name='ticket_admin_outstanding_charges'),
    url(r'^request/submit/$', requests.RequestHandler.as_view(), name='request'),

    url(r'^ticket/$',      perm('user', ticket.views.TicketListMyOpen), name='ticket_list'),
    url(r'^ticket/(?P<page>\d+)/$',      perm('user', ticket.views.TicketListMyOpen), name='ticket_list'),
    url(r'^ticket/submit/$',                perm('user', ticket.views.TicketRequest), name='ticket_submit'),
    url(r'^ticket/(?P<ticket_id>[0-9]+)/details/$', 
                                            perm('user', ticket.views.TicketDetail), name='ticket_details'),
    url(r'^ticket/manage/(?P<pk>[0-9]+)/settings/$', ticket.views.TicketAdminSettingsHandler.as_view(), name='ticket_admin_settings'),
    url(r'^ticket/manage/(?P<ticket_id>[0-9]+)/edit/$', 
                                            perm('user', ticket.views.TicketRequest), name='ticket_edit'),
    url(r'^ticket/manage/company_ownership/(?P<pk>[0-9]+)/edit/$', 
                                            perm('user', ticket.views.CompanyTicketUpdate), name='company_ownership_ticket_edit'),
    url(r'^ticket/manage/person_ownership/(?P<pk>[0-9]+)/edit/$', 
                                            perm('user', ticket.views.PersonTicketUpdate), name='person_ownership_ticket_edit'),
    url(r'^ticket/manage/other/(?P<pk>[0-9]+)/edit/$', 
                                            perm('user', ticket.views.OtherTicketUpdate), name='other_ticket_edit'),
    url(r'^ticket/(?P<pk>[0-9]+)/close/$',  perm('user', ticket.views.TicketActionCloseHandler), name='ticket_close'),
    url(r'^ticket/(?P<pk>[0-9]+)/open/$',   perm('user', ticket.views.TicketActionOpenHandler), name='ticket_open'),
    url(r'^ticket/(?P<pk>[0-9]+)/cancel/$', perm('user', ticket.views.TicketActionCancelHandler), name='ticket_cancel'),
    url(r'^ticket/(?P<pk>[0-9]+)/join/$',   perm('volunteer', ticket.views.TicketActionJoinHandler), name='ticket_join'),
    url(r'^ticket/(?P<pk>[0-9]+)/leave/$',  perm('volunteer', ticket.views.TicketActionLeaveHandler), name='ticket_leave'),
    url(r'^ticket/(?P<pk>[0-9]+)/updateremove/$',  perm('volunteer', ticket.views.TicketUpdateRemoveHandler), name='ticket_update_remove'),

    url(r'^ticket/fees/users/$',            perm('staff', ticket.views.TicketUserFeesOverview), name='ticket_fees_users'),
    url(r'^ticket/fees/networks/$',         perm('staff', ticket.views.TicketNetworkFeesOverview), name='ticket_fees_networks'),
    url(r'^ticket/fees/budgets/$',          perm('staff', ticket.views.TicketBudgetFeesOverview), name='ticket_fees_budgets'),

    url(r'^_validation/request/$',          perm('user', ticket.validators.ValidateTicketRequest), name='ajax_validate_request'),

    url(r'^databases/$',                    perm('any', databases.ExternalDatabaseList), name='externaldb_list'),
    url(r'^databases/add/$',                perm('staff', databases.ExternalDatabaseAdd), name='externaldb_add'),
    url(r'^databases/edit/(?P<id>[0-9]+)/$',perm('staff', databases.ExternalDatabaseEdit), name='externaldb_edit'),
    url(r'^databases/view/(?P<id>[0-9]+)/$',perm('any', databases.ExternalDatabaseDetail), name='externaldb_detail'),
    url(r'^databases/delete/(?P<id>[0-9]+)/$', 
                                            perm('admin', databases.ExternalDatabaseDelete), name='externaldb_delete'),

    url(r'^accounts/login/$', 'django.contrib.auth.views.login', {'template_name': 'registration/login.jinja'}, name='login'),
    url(r'^accounts/logout/', 'django.contrib.auth.views.logout', {'template_name': 'registration/logout.jinja'}, name='logout'),
    url(r'^accounts/users/$',               perm('admin', accounts.UserList), name='userprofile_list'),
    url(r'^accounts/request/$',             perm('any', accounts.AccountRequestHome), name='request_account_home'),
    url(r'^accounts/request/list/$',        perm('admin', accounts.AccountRequestList), name='request_account_list'),
    url(r'^accounts/profile/$',             perm('user', accounts.ProfileUpdate), name='profile'),
    url(r'^accounts/profile/(?P<pk>[0-9]+)/$',
                                            perm('admin', accounts.ProfileUpdate), name='profile'),
    url(r'^accounts/profile/(?P<username>.+)/$',
                                            perm('admin', accounts.ProfileUpdate), name='profile'),
    url(r'^accounts/setlanguage/(?P<lang>[a-zA-Z]{2})/$',
                                            perm('user', accounts.ProfileSetLanguage), name='account_set_language'),
    url(r'^accounts/requester/$',           perm('any', accounts.AccountRequest), name='request_account'),
    url(r'^accounts/volunteer/$',           perm('any', accounts.AccountVolunteer), name='volunteer_account'),

    url(r'^accounts/password/change/$', auth_views.password_change, {'template_name': 'registration/password_change_form.jinja'}, name='auth_password_change'),
    url(r'^accounts/password/change/done/$', auth_views.password_change_done, {'template_name': 'registration/password_change_done.jinja'}, name='auth_password_change_done'), 
    url(r'^accounts/password/reset/$', auth_views.password_reset, {'template_name': 'registration/password_reset_form.jinja'}, name='auth_password_reset'),
    url(r'^accounts/password/reset/confirm/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$', auth_views.password_reset_confirm, {'template_name': 'registration/password_reset_confirm.jinja'}, name='auth_password_reset_confirm'),
    url(r'^accounts/password/reset/complete/$', auth_views.password_reset_complete, {'template_name': 'registration/password_reset_complete.jinja'}, name='auth_password_reset_complete'),
    url(r'^accounts/password/reset/done/$', auth_views.password_reset_done, {'template_name': 'registration/password_reset_done.jinja'}, name='auth_password_reset_done'),

    url(r'^accounts/activate/complete/$', TemplateView.as_view(template_name='registration/activation_complete.jinja'), name='registration_activation_complete'),
    url(r'^accounts/activate/(?P<activation_key>w+)/$', ActivationView.as_view(template_name='registration/activation_form.jinja'), name='registration_activate'),
    url(r'^accounts/register/$', RegistrationView.as_view(template_name='registration/registration_form.jinja'), name='registration_register'),
    url(r'^accounts/register/complete/$', TemplateView.as_view(template_name='registration/registration_complete.jinja'), name='registration_complete'),
    url(r'^accounts/register/closed/$',  TemplateView.as_view(template_name='registration/registration_closed.jinja'), name='registration_disallowed'),

    url(r'^podaci/', include('podaci.urls')),
    url(r'^osoba/', include('osoba.urls')),
    url(r'^robots/', include('robots.urls')),

    url(r'^i18n/', include('django.conf.urls.i18n')),
    url(r'^jsi18n/$', 'django.views.i18n.javascript_catalog', js_info_dict),
    url(r'^jsi18n/(?P<packages>\S+?)/$', 'django.views.i18n.javascript_catalog'),

    url(r'^json/all_users/$', requests.Select2AllHandler.as_view(), name='select2_all_users'),
)

handler400 = errors._400
handler403 = errors._403
handler404 = errors._403
handler500 = errors._500


"""
    url(r'/file/sharing/<entity_id:.+>/', h.SharingHandler, name='share_files'),
    url(r'/file/oauth_success/', h.OAuthSuccess, name='oauth_success'),
    url(r'/tasks/groups_sync/', t.GroupSyncTask, name='groups_sync_task'),
    url(r'/entity/view/', h.ViewEntityHandler, name='entity_view'),
    url(r'/admin/approve_account/<account_request_key:.+>/', h.AccountRequestActionHandler, name='account_request_approval'),
    url(r'/admin/inline_relationship/', h.InlineRelationshipHandler, name='inline_relationship'),
    url(r'/admin/relationship_types/', h.RelationshipTypesHandler, name='relationship_types'),
    url(r'/import_external_dbs/', h.ImportExternalDBsHandler, name='import_external_dbs'),
    url(r'/country_report/', h.CountryReportHandler, name='country_report'),
    url(r'/fixitall/', h.TemporaryFixHandler, name='temporary_fix'),
    url(r'/migrate_account_requests/', h.MigrateAccountRequestsHandler, name='migrate_account_requests'),
    # url(rdrive_decorator.callback_path, drive_decorator.callback_handler()), h.RequestMailHandler.mapping(),
    url(r'/_select2/responder/', h.Select2ResponderHandler, name='select2_responder'),
    url(r'/admin/usergroups.csv', h.UserGroupsCsvHandler, name='usergroups_csv'),
    url(r'/admin/test_search', h.TestSearchHandler, name='test_search')
"""
