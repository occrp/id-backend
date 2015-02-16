from django.conf.urls import patterns, include, url
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView

from id import databases, requests, search, accounts
from id import validation, admin, tasks, files
# from id.google_apis.drive import drive_decorator

from django.contrib import admin as django_admin
django_admin.autodiscover()

js_info_dict = {
    'packages': ('id',),
}

urlpatterns = patterns('',
    url(r'^$', TemplateView.as_view(template_name="splash.html"), name="home"),
    url(r'^about/$', TemplateView.as_view(template_name="about_us.html"), name='about_us'),

    url(r'^admin/$', admin.Panel.as_view(), name='admin_panel'),
    url(r'^admin/company/list$', admin.CompanyList.as_view(), name='company_list'),
    url(r'^admin/person/list$', admin.PersonList.as_view(), name='person_list'),
    url(r'^admin/location/list$', admin.LocationList.as_view(), name='location_list'),
    url(r'^admin/relationship/list$', admin.RelationshipList.as_view(), name='relationship_list'),

    url(r'^admin/storage/$', admin.Storage.as_view(), name='admin_storage'),
    url(r'^admin/statistics/$', admin.Statistics.as_view(), name='statistics'),
    url(r'^admin/django/', include(django_admin.site.urls)),

    url(r'^search/$', search.CombinedSearchHandler.as_view(), name="search"),
    url(r'^search/entities/$', search.CombinedSearchHandler.as_view(), name='search_entities'), # still needed for ajax only

    url(r'^request/$', requests.RequestListHandler.as_view(), name='request_list'),
    url(r'^request/(?P<ticket_id>[0-9]+)/details/$', requests.RequestDetailsHandler.as_view(), name='request_details'),
    url(r'^request/(?P<ticket_id>[0-9]+)/close/$', requests.RequestCloseHandler.as_view(), name='request_close'),
    url(r'^request/(?P<ticket_id>[0-9]+)/cancel/$', requests.RequestCancelHandler.as_view(), name='request_cancel'),
    url(r'^request/(?P<ticket_id>[0-9]+)/delete/$', requests.RequestDeleteHandler.as_view(), name='request_delete'),
    url(r'^request/(?P<ticket_id>[0-9]+)/flag/$', requests.RequestFlagHandler.as_view(), name='request_flag'),
    url(r'^request/(?P<ticket_id>[0-9]+)/reopen/$', requests.RequestReopenHandler.as_view(), name='request_reopen'),
    url(r'^request/(?P<ticket_id>[0-9]+)/pay/$', requests.RequestPaidHandler.as_view(), name='request_mark_paid'),
    url(r'^request/(?P<ticket_id>[0-9]+)/charge/$', requests.RequestAddChargeHandler.as_view(), name='request_charge_add'),
    url(r'^request/(?P<ticket_id>[0-9]+)/entity/add/$', requests.RequestAddEntityHandler.as_view(), name='request_entity_add'),
    url(r'^request/(?P<ticket_id>[0-9]+)/entity/remove/$', requests.RequestRemoveEntityHandler.as_view(), name='request_entity_remove'),
    url(r'^request/(?P<ticket_id>[0-9]+)/join/$', requests.RequestJoinHandler.as_view(), name='ticket_join'),
    url(r'^request/(?P<ticket_id>[0-9]+)/leave/$', requests.RequestLeaveHandler.as_view(), name='ticket_leave'),
    url(r'^request/submit/$', requests.RequestHandler.as_view(), name='request'),
    url(r'^request/request_unauthorized/$', requests.RequestUnauthorized.as_view(), name='request_unauthorized'),
    url(r'^request/respond/$', requests.ResponseListHandler.as_view(), name='response_list'),
    url(r'^request/public/$', requests.PublicListHandler.as_view(), name='public_list'),
    url(r'^request/manage/unassigned/$', requests.AdminUnassignedTicketsHandler.as_view(), name='ticket_admin_unassigned'),
    url(r'^request/manage/deadline/$', requests.AdminDeadlineTicketsHandler.as_view(), name='ticket_admin_deadline'),
    url(r'^request/manage/history/$', requests.AdminHistoryTicketsHandler.as_view(), name='ticket_admin_history'),
    url(r'^request/manage/flagged/$', requests.AdminFlaggedTicketsHandler.as_view(), name='ticket_admin_flagged'),
    url(r'^request/manage/(?P<ticket_id>[0-9]+)/edit/$', requests.RequestHandler.as_view(), name='ticket_edit'),
    url(r'^request/manage/(?P<ticket_id>[0-9]+)/settings/$', requests.AdminSettingsHandler.as_view(), name='ticket_admin_settings'),
    url(r'^request/charges/customer/$', requests.AdminCustomerChargesHandler.as_view(), name='ticket_admin_customer_charges'),
    url(r'^request/charges/(?P<charge_key>.+)/reconcile/$', requests.AdminChargeReconcileInlineHandler.as_view(), name='ticket_admin_reconcile_charges'),
    url(r'^request/charges/outstanding/$', requests.AdminOutstandingChargesHandler.as_view(), name='ticket_admin_outstanding_charges'),
    url(r'^request/submit/$', requests.RequestHandler.as_view(), name='request'),

    url(r'^_validation/company/$', validation.ValidateCompany.as_view(), name='ajax_validate_company'),
    url(r'^_validation/person/$', validation.ValidatePerson.as_view(), name='ajax_validate_person'),
    url(r'^_validation/location/$', validation.ValidateLocation.as_view(), name='ajax_validate_location'),
    url(r'^_validation/request/$', validation.ValidateRequest.as_view(), name='ajax_validate_request'),

    url(r'^databases/$', databases.ExternalDatabaseList.as_view(), name='externaldb_list'),
    url(r'^databases/add/$', databases.ExternalDatabaseAdd.as_view(), name='externaldb_add'),
    url(r'^databases/edit/(?P<id>[0-9]+)/$', databases.ExternalDatabaseEdit.as_view(), name='externaldb_edit'),
    url(r'^databases/view/(?P<id>[0-9]+)/$', databases.ExternalDatabaseDetail.as_view(), name='externaldb_detail'),
    url(r'^databases/delete/(?P<id>[0-9]+)/$', databases.ExternalDatabaseDelete.as_view(), name='externaldb_delete'),

    url(r'^accounts/', include('registration.backends.default.urls')),
    url(r'^accounts/users/$', accounts.UserList.as_view(), name='userprofile_list'),
    url(r'^accounts/request/$', accounts.AccountRequestHome.as_view(), name='request_account_home'),
    url(r'^accounts/request/list/$', accounts.AccountRequestList.as_view(), name='request_account_list'),
    url(r'^accounts/profile/$', login_required(accounts.ProfileUpdate.as_view()), name='profile'),
    url(r'^accounts/profile/(?P<pk>[0-9]+)/$', login_required(accounts.ProfileView.as_view()), name='profile'),
    url(r'^accounts/profile/(?P<username>.+)/$', login_required(accounts.ProfileView.as_view()), name='profile'),
    url(r'^accounts/requester/$', login_required(accounts.AccountRequest.as_view()), name='request_account'),
    url(r'^accounts/volunteer/$', login_required(accounts.AccountVolunteer.as_view()), name='volunteer_account'),
    url(r'^accounts/login/$', 'django.contrib.auth.views.login', {'template_name': 'login.html'}, name='login'),
    # url(r'/post_login_redirect', accounts.PostLoginRedirectHandler, name='post_login_redirect'),
    # url(r'/complete_login', h.CompleteLoginHandler, name="complete_login"),

    url(r'^file/list/(?P<folder_id>.+)/$', files.ListFilesHandler.as_view(), name='list_files'),
    url(r'^file/remove/$', files.RemoveFileHandler.as_view(), name='remove_file'),
    url(r'^file/upload/$', files.UploadFileHandler.as_view(), name='upload_files'),
    url(r'^file/upload/direct/$', files.DirectUploadFileHandler.as_view(), name='upload_direct'),
    url(r'^file/upload_check/$', files.UploadCheck.as_view(), name='upload_check'),

    url(r'^podaci/', include('podaci.urls')),

    url(r'^jsi18n/$', 'django.views.i18n.javascript_catalog', js_info_dict),
    url(r'^jsi18n/(?P<packages>\S+?)/$', 'django.views.i18n.javascript_catalog'),

    url(r'^json/all_users/$', requests.Select2AllHandler.as_view(), name='select2_all_users'),

)


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
