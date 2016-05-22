from django.conf.urls import patterns, include, url
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView
from core.auth import perm

from id import requests

import ticket.validators
import ticket.views

urlpatterns = patterns('',
    url(r'^all_open/$',              perm('staff', ticket.views.TicketListAllOpen), name='ticket_all_open_list'),
    url(r'^all_open/(?P<page>\d+)/$',perm('staff', ticket.views.TicketListAllOpen), name='ticket_all_open_list'),
    url(r'^all_closed/$',            perm('staff', ticket.views.TicketListAllClosed), name='ticket_all_closed_list'),
    url(r'^all_closed/(?P<page>\d+)/$',
                                     perm('staff', ticket.views.TicketListAllClosed), name='ticket_all_closed_list'),
    url(r'^$',                       perm('user', ticket.views.TicketListMyOpen), name='ticket_list'),
    url(r'^(?P<page>\d+)/$',         perm('user', ticket.views.TicketListMyOpen), name='ticket_list'),
    url(r'^closed/$',                perm('user', ticket.views.TicketListMyClosed), name='ticket_closed_list'),
    url(r'^closed/(?P<page>\d+)/$',  perm('user', ticket.views.TicketListMyClosed), name='ticket_closed_list'),
    url(r'^assigned/$',              perm('volunteer', ticket.views.TicketListMyAssigned), name='ticket_assigned_list'),
    url(r'^assigned/(?P<page>\d+)/$',perm('volunteer', ticket.views.TicketListMyAssigned), name='ticket_assigned_list'),
    url(r'^assigned/closed/$',       perm('volunteer', ticket.views.TicketListMyAssignedClosed), name='ticket_assigned_closed_list'),
    url(r'^assigned/closed/(?P<page>\d+)/$', perm('volunteer', ticket.views.TicketListMyAssignedClosed), name='ticket_assigned_closed_list'),
    url(r'^public/$',                perm('user', ticket.views.TicketListPublic), name='ticket_public_list'),
    url(r'^public/(?P<page>\d+)/$',  perm('user', ticket.views.TicketListPublic), name='ticket_public_list'),
    url(r'^public/closed/$',         perm('user', ticket.views.TicketListPublicClosed), name='ticket_public_closed_list'),
    url(r'^public/closed/(?P<page>\d+)/$',
                                     perm('user', ticket.views.TicketListPublicClosed), name='ticket_public_closed_list'),
    url(r'^unassigned/$',            perm('user', ticket.views.TicketListUnassigned), name='ticket_unassigned_list'),
    url(r'^unassigned/(?P<page>\d+)/$',
                                     perm('user', ticket.views.TicketListUnassigned), name='ticket_unassigned_list'),
    url(r'^upcoming_deadline/$',     perm('user', ticket.views.TicketListUpcomingDeadline), name='ticket_deadline_list'),
    url(r'^upcoming_deadline/(?P<page>\d+)/$',
                                     perm('user', ticket.views.TicketListUpcomingDeadline), name='ticket_deadline_list'),
    url(r'^user/(?P<user_id>\d+)/$', perm('staff', ticket.views.TicketListUser), name='ticket_user_list'),
    url(r'^user/(?P<user_id>\d+)/(?P<page>\d+)/$',
                                     perm('staff', ticket.views.TicketListUser), name='ticket_country_list'),
    url(r'^country/$',               perm('staff', ticket.views.TicketCountries), name='ticket_countries'),
    url(r'^country/(?P<country>.+)/$', perm('staff', ticket.views.TicketListCountry), name='ticket_user_list'),
    url(r'^country/(?P<country>.+)/(?P<page>\d+)/$',
                                     perm('staff', ticket.views.TicketListCountry), name='ticket_country_list'),

    url(r'^submit/$',                perm('user', ticket.views.TicketRequest), name='ticket_submit'),
    url(r'^manage/(?P<ticket_id>[0-9]+)/details/$',
                                     perm('user', ticket.views.TicketDetail), name='ticket_details'),
    url(r'^manage/(?P<pk>[0-9]+)/settings/(?P<redirect>[a-z_]+)/$', ticket.views.TicketAdminSettingsHandler.as_view(), name='ticket_admin_settings'),
    url(r'^manage/(?P<ticket_id>[0-9]+)/edit/$',
                                     perm('user', ticket.views.TicketRequest), name='ticket_edit'),
    url(r'^manage/company_ownership/(?P<pk>[0-9]+)/edit/$',
                                     perm('user', ticket.views.CompanyTicketUpdate), name='company_ownership_ticket_edit'),
    url(r'^manage/person_ownership/(?P<pk>[0-9]+)/edit/$',
                                     perm('user', ticket.views.PersonTicketUpdate), name='person_ownership_ticket_edit'),
    url(r'^manage/other/(?P<pk>[0-9]+)/edit/$',
                                     perm('user', ticket.views.OtherTicketUpdate), name='other_ticket_edit'),

    url(r'^manage/workload$',        perm('staff', ticket.views.TicketResolutionWorkload), name='ticket_researcher_workload'),
    url(r'^manage/worktime$',        perm('staff', ticket.views.TicketResolutionTime), name='ticket_resolution_time'),
    url(r'^manage/report$',          perm('staff', ticket.views.TicketReport), name='ticket_monthly_report'),
    url(r'^(?P<pk>[0-9]+)/close/$',  perm('user', ticket.views.TicketActionClose), name='ticket_close'),
    url(r'^(?P<pk>[0-9]+)/open/$',   perm('user', ticket.views.TicketActionOpen), name='ticket_open'),
    url(r'^(?P<pk>[0-9]+)/cancel/$', perm('user', ticket.views.TicketActionCancel), name='ticket_cancel'),
    url(r'^(?P<pk>[0-9]+)/join/$',   perm('volunteer', ticket.views.TicketActionJoin), name='ticket_join'),
    url(r'^(?P<pk>[0-9]+)/leave/$',  perm('volunteer', ticket.views.TicketActionLeave), name='ticket_leave'),
    url(r'^(?P<pk>[0-9]+)/unassign/$', ticket.views.TicketActionUnassign, name='ticket_unassign'),
    url(r'^(?P<pk>[0-9]+)/assign/$', ticket.views.TicketActionAssign, name='ticket_assign'),
    url(r'^(?P<pk>[0-9]+)/remove_files/$', ticket.views.TicketActionRemoveFiles, name='ticket_files_remove'),
    url(r'^(?P<pk>[0-9]+)/updateremove/$',
                                     perm('volunteer', ticket.views.TicketUpdateRemoveHandler), name='ticket_update_remove'),

    url(r'^fees/users/$',            perm('staff', ticket.views.TicketUserFeesOverview), name='ticket_fees_users'),
    url(r'^fees/networks/$',         perm('staff', ticket.views.TicketNetworkFeesOverview), name='ticket_fees_networks'),
    url(r'^fees/budgets/$',          perm('staff', ticket.views.TicketBudgetFeesOverview), name='ticket_fees_budgets'),
    url(r'^_validation/request/$',   perm('user', ticket.validators.ValidateTicketRequest), name='ajax_validate_request'),

    # TODO: FIXME THESE SHOULD NOT BE REFERENCING REQUESTS
    url(r'^(?P<pk>[0-9]+)/pay/$',    perm('staff', ticket.views.TicketMarkPaid), name='request_mark_paid'),
    url(r'^(?P<pk>[0-9]+)/charge/$', perm('staff', ticket.views.TicketAddCharge), name='request_charge_add'),
    url(r'^(?P<pk>[0-9]+)/charge/modify/$', perm('staff', ticket.views.TicketModifyCharge), name='request_charge_modify'),
    url(r'^fees/outstanding/$',      perm('staff', ticket.views.AdminOustandingChargesList), name='ticket_admin_outstanding_charges'),
    url(r'^fees/outstanding/(?P<page>\d+)/$', perm('staff', ticket.views.AdminOustandingChargesList), name='ticket_admin_outstanding_charges'),
)
