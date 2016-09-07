from __future__ import absolute_import
from datetime import datetime, timedelta
import logging

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.urlresolvers import reverse, reverse_lazy
from django.core.exceptions import PermissionDenied
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.db.models import Count, Sum
from django.db.models import Q
from django.http import Http404
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.http import JsonResponse
from django.http import FileResponse
from django.middleware.csrf import get_token
from django.template.loader import render_to_string
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ugettext
from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView, UpdateView
from rules.contrib.views import PermissionRequiredMixin

from accounts.models import Network, Profile
from core.models import Notification
from core.mixins import CSVorJSONResponseMixin, PrettyPaginatorMixin

from .mixins import TicketUpdateMixin, perform_ticket_update
from .mixins import transition_ticket_from_new
from .models import Ticket, PersonTicket, CompanyTicket, OtherTicket
from .models import TicketUpdate, TicketCharge, Budget, TicketAttachment
from . import forms
from . import constants

log = logging.getLogger(__name__)


class AdminOustandingChargesList(PrettyPaginatorMixin, CSVorJSONResponseMixin, TemplateView):
    template_name = 'tickets/admin/admin_charges_outstanding.jinja'
    page_name = "Outstanding Charges"
    ticket_list_name = ""
    charges = []
    page_number = 1
    page_size = 10
    page_buttons = 5
    page_buttons_padding = 2
    paginator = None
    url_name = 'ticket_admin_outstanding_charges'
    url_args = {}
    CONTEXT_ITEMS_KEY = "tickets"
    CONTEXT_TITLE_KEY = "page_name"

    def get_context_data(self, **kwargs):
        self.filter_terms = self.request.GET.get("filter", '')

        if 'page' in kwargs:
            self.page_number = int(kwargs.pop('page'))
            if self.page_number is None:
                self.page_number = 1

        context = {
            'page_name': self.page_name,
            'charges': self.get_paged_charges(self.page_number),
            'paginator_object': self.create_pretty_pagination_object(self.paginator,
                                                                     self.page_number,
                                                                     self.page_buttons,
                                                                     self.page_buttons_padding,
                                                                     self.url_name,
                                                                     self.url_args),
            'page_number': self.page_number,
            'ticket_figures': self.get_ticket_list_figures(),
            'filter_terms': self.filter_terms
        }

        return context

    def get_ticket_list_figures(self):
        ticket_figures = {
            'all_open': TicketListAllOpen().get_ticket_set(self.request.user).count(),
            'all_closed': TicketListAllClosed().get_ticket_set(self.request.user).count(),
            'my_open': TicketListMyOpen().get_ticket_set(self.request.user).count(),
            'my_closed': TicketListMyClosed().get_ticket_set(self.request.user).count(),
            'my_assigned': TicketListMyAssigned().get_ticket_set(self.request.user).count(),
            'my_assigned_closed': TicketListMyAssignedClosed().get_ticket_set(self.request.user).count(),
            'public': TicketListPublic().get_ticket_set(self.request.user).count(),
            'public_closed': TicketListPublicClosed().get_ticket_set(self.request.user).count(),
            'unassigned': TicketListUnassigned().get_ticket_set(self.request.user).count(),
            'upcoming_deadline': TicketListUpcomingDeadline().get_ticket_set(self.request.user).count(),
            'oustanding_charges': AdminOustandingChargesList().get_charges_set().count()
        }

        return ticket_figures

    def get_paged_charges(self, page_number):
        self.set_paginator_object()

        try:
            paged_charges = self.paginator.page(page_number)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            paged_charges = self.paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results
            paged_charges = self.paginator.page(self.paginator.num_pages)

        return paged_charges

    def get_charges_set(self):
        return TicketCharge.objects.filter(reconciled=False)

    def set_paginator_object(self):
        charges_set = self.get_charges_set()

        self.paginator = Paginator(charges_set, self.page_size)

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(AdminOustandingChargesList, self).dispatch(*args, **kwargs)


class CompanyTicketUpdate(TicketUpdateMixin, UpdateView,
                          PermissionRequiredMixin):
    model = CompanyTicket
    template_name = 'tickets/request.jinja'
    form_class = forms.CompanyTicketForm
    permission_required = 'ticket.change_ticket'

    def get_context_data(self, **kwargs):
        context = super(CompanyTicketUpdate, self).get_context_data(**kwargs)
        context['ticket'] = self.get_object()
        context['company_ownership_form'] = context['form']
        return context

    def __init__(self, *args, **kwargs):
        super(CompanyTicketUpdate, self).__init__(*args, **kwargs)


class OtherTicketUpdate(TicketUpdateMixin, UpdateView,
                        PermissionRequiredMixin):
    model = OtherTicket
    template_name = 'tickets/request.jinja'
    form_class = forms.OtherTicketForm
    permission_required = 'ticket.change_ticket'

    def get_context_data(self, **kwargs):
        context = super(OtherTicketUpdate, self).get_context_data(**kwargs)
        context['ticket'] = self.get_object()
        context['other_form'] = context['form']
        return context

    def __init__(self, *args, **kwargs):
        super(OtherTicketUpdate, self).__init__(*args, **kwargs)


class PersonTicketUpdate(TicketUpdateMixin, UpdateView,
                         PermissionRequiredMixin):
    model = PersonTicket
    template_name = 'tickets/request.jinja'
    form_class = forms.PersonTicketForm
    permission_required = 'ticket.change_ticket'

    def get_context_data(self, **kwargs):
        context = super(PersonTicketUpdate, self).get_context_data(**kwargs)
        context['ticket'] = self.get_object()
        context['person_ownership_form'] = context['form']
        return context

    def __init__(self, *args, **kwargs):
        super(PersonTicketUpdate, self).__init__(*args, **kwargs)


class TicketActionBaseHandler(TicketUpdateMixin, UpdateView,
                              PermissionRequiredMixin):
    model = Ticket
    form_class = forms.TicketCancelForm
    permission_required = 'ticket.change_ticket'

    success_messages = None
    failure_messages = None
    force_invalid = False

    def perform_invalid_action(self, form):
        return

    def perform_valid_action(self, form):
        return

    def form_invalid(self, form):
        self.perform_invalid_action(form)
        return HttpResponseRedirect(reverse('ticket_details',
                                    kwargs={"ticket_id": self.object.id}))

    def form_valid(self, form):
        self.perform_valid_action(form)

        if self.force_invalid is True:
            return self.form_invalid(form)

        return super(TicketActionBaseHandler, self).form_valid(form, self.success_messages)

    def get_success_url(self):
        ticket = self.get_object()
        return reverse_lazy('ticket_details', kwargs={'ticket_id': ticket.id})


class TicketActionCancel(TicketActionBaseHandler):
    form_class = forms.TicketEmptyForm
    permission_required = 'ticket.revoke_ticket'

    def perform_invalid_action(self, form):
        messages.error(self.request, _('A reason must be supplied to cancel the ticket.'))

    def perform_valid_action(self, form):
        ticket = self.object
        ticket.status = constants.get_choice('Cancelled', constants.TICKET_STATUS)
        self.perform_ticket_update(ticket, 'Cancelled', '')
        return super(TicketActionCancel, self).perform_valid_action(form)


class TicketActionClose(TicketActionBaseHandler):
    form_class = forms.TicketEmptyForm
    permission_required = 'ticket.change_ticket'

    def perform_invalid_action(self, form):
        messages.error(self.request, _('An error came up processing your close request.'))

    def perform_valid_action(self, form):
        ticket = self.object
        ticket.status = constants.get_choice('Closed', constants.TICKET_STATUS)
        self.perform_ticket_update(ticket, 'Closed', '')
        return super(TicketActionClose, self).perform_valid_action(form)


class TicketActionJoin(TicketActionBaseHandler):
    form_class = forms.TicketEmptyForm
    permission_required = 'ticket.join_ticket'

    def perform_invalid_action(self, form):
        messages.error(self.request, _('There was an error adding you to the ticket.'))

    def perform_valid_action(self, form):
        ticket = self.object
        adduser = None

        if self.request.user.is_staff or self.request.user.is_superuser:
            uid = self.request.POST.get("user", self.request.user.id)
            adduser = get_user_model().objects.get(id=uid)
            ticket.responders.add(adduser)
            adduser.notifications_subscribe('id:ticket:ticket:%d:*' % ticket.id)

            self.success_messages = [_('You have successfully been added to the ticket.')]
            self.perform_ticket_update(ticket, 'Responder Joined', adduser.display_name + unicode(_(' has joined the ticket')))
            self.transition_ticket_from_new(ticket)
            # #tag.add_user(adduser, True)
            return super(TicketActionJoin, self).perform_valid_action(form)
        else:
            self.perform_invalid_action(form)


def TicketActionAssign(request, pk):
    ticket = Ticket.objects.get(id=int(pk))
    if not request.user.has_perm('ticket.manage_ticket', ticket):
        raise PermissionDenied
    user = get_user_model().objects.get(id=request.POST.get('user'))
    ticket.responders.add(user)
    user.notifications_subscribe('id:ticket:ticket:%d:*' % ticket.id)
    perform_ticket_update(ticket, 'Responder Joined', user.display_name + unicode(_(' has joined the ticket')), user)

    transition_ticket_from_new(ticket)

    if request.user.id == user.id:
        success_message = ugettext("You have successfully been added to the ticket")
    else:
        success_message = user.display_name + ugettext(' has been added to the ticket.')

    # Manually notify the assigned user that
    # he has been assigned to the ticket.
    n = Notification()
    n.create(user, 'id:ticket:ticket:%d:join' % ticket.id,
             "%s added you to ticket %s" % (request.user, ticket.summary),
             'ticket_details', {'ticket_id': ticket.id})

    return JsonResponse({'message': success_message,
                        'status': 'success'})


def TicketActionUnassign(request, pk):
    ticket = Ticket.objects.get(id=int(pk))
    if not request.user.has_perm('ticket.manage_ticket', ticket):
        raise PermissionDenied

    user = get_user_model().objects.get(id=request.POST.get('user'))

    if user in ticket.responders.all():
        ticket.responders.remove(user)
        perform_ticket_update(ticket, 'Responder Left', user.display_name + ' has left the ticket', user)

        if request.user.id == user.id:
            success_message = ugettext("You have successfully been removed from the ticket")
        else:
            success_message = user.display_name + ugettext(' has been removed from the ticket.')

        user.notifications_unsubscribe('id:ticket:ticket:%d:*' % ticket.id)

        return JsonResponse({'message': success_message,
                            'status': 'success'})
    else:
        if request.user.id == user.id:
            error_message = ugettext('There was an error removing you from the ticket.')
        else:
            error_message = ugettext('There was an error removing the user from the ticket.')

        return JsonResponse({'message': error_message,
                             'status': 'error'},
                            status=403)


class TicketActionLeave(TicketActionBaseHandler):
    form_class = forms.TicketEmptyForm
    permission_required = 'ticket.leave_ticket'

    def form_valid(self, form):
        if self.request.is_ajax():
            self.assign_user(form, False)

            if not self.force_invalid:
                return JsonResponse({'message': ugettext('You have successfully been removed from the ticket.'),
                                     'status': 'success'})
            else:
                return JsonResponse({'message': ugettext('There was an error removing you from the ticket'),
                                     'status': 'error'},
                                    status=403)

        else:
            return super(TicketActionLeave, self).form_valid(form)

    def perform_invalid_action(self, form):
        messages.error(self.request, _('There was an error removing you from the ticket.'))

    def perform_valid_action(self, form):
        self.assign_user(form, True)

    def assign_user(self, form, is_ajax_call):
        ticket = self.object

        # tag = ticket.get_tag()

        if self.request.user in ticket.responders.all():
            ticket.responders.remove(self.request.user)
            self.request.user.notifications_unsubscribe('id:ticket:ticket:%d:*' % ticket.id)
            self.success_messages = [_('You have successfully been removed from the ticket.')]
            self.perform_ticket_update(ticket, 'Responder Left', self.request.user.display_name + unicode(_(' has left the ticket')))

            if is_ajax_call:
                self.success_messages = [_('You have successfully been removed from the ticket.')]
                return super(TicketActionLeave, self).perform_valid_action(form)
        else:
            self.force_invalid = True


class TicketActionOpen(TicketActionBaseHandler):
    permission_required = 'ticket.change_ticket'

    def perform_invalid_action(self, form):
        messages.error(self.request, _('A reason must be supplied to (re)open the ticket.'))

    def perform_valid_action(self, form):
        ticket = self.object

        if ticket.responders.count() == 0:
            ticket.status = constants.get_choice('New', constants.TICKET_STATUS)
        else:
            ticket.status = constants.get_choice('In Progress', constants.TICKET_STATUS)

        self.perform_ticket_update(ticket, 'Opened', form.cleaned_data['reason'])

        return super(TicketActionOpen, self).perform_valid_action(form)


class TicketAddCharge(TicketActionBaseHandler):
    form_class = forms.RequestChargeForm
    permission_required = 'ticket.manage_ticket'

    def perform_invalid_action(self, form):
        messages.error(self.request, _('Error adding charge.'))

    def perform_valid_action(self, form):
        charge = TicketCharge(
            ticket=self.object,
            user=self.request.user,
            item=form.cleaned_data['item'],
            cost=form.cleaned_data['cost'],
            cost_original_currency=form.cleaned_data['cost_original_currency'],
            original_currency=form.cleaned_data['original_currency']
        )

        if form.cleaned_data['reconciled']:
            charge.reconciled = True
            charge.reconciled_date = form.cleaned_data['reconciled_date']

        charge.save()

        self.perform_ticket_update(self.object,
                                   'Charge Added',
                                   "$%.2f" % float(form.cleaned_data['cost']) + " - " + form.cleaned_data['item'])
        return super(TicketAddCharge, self).perform_valid_action(form)


class TicketModifyCharge(TicketUpdateMixin, UpdateView):
    model = TicketCharge
    template_name = 'modals/form_basic.jinja'
    form_class = forms.RequestChargeForm
    permission_required = 'ticket.manage_ticket'

    # it should be noted here that this is ugly
    # when using the get, the pk stands for the
    def get(self, request, pk, status='success'):
        super(TicketModifyCharge, self).get(self, request)
        t = render_to_string('modals/form_basic.jinja',
                             self.get_context_data())
        return JsonResponse({'status': status, 'html': t})

    def get_context_data(self, **kwargs):
        context = super(TicketModifyCharge, self).get_context_data(**kwargs)
        context['csrf'] = get_token(self.request)
        context['form_action'] = reverse_lazy('request_charge_modify', kwargs={'pk': self.object.id})
        context['form'] = self.get_form(self.form_class)
        return context

    def form_invalid(self, form):
        self.perform_invalid_action(form)
        return HttpResponse('error updating charge', status_code=400)

    def form_valid(self, form):
        self.perform_valid_action(form)

        # just to get the ticket to save
        super(TicketModifyCharge, self).form_valid(form, [_('Charge successfully updated.')])

        return JsonResponse({'success': 'success'})

    def perform_invalid_action(self, form):
        messages.error(self.request, _('Error updating charge.'))

    def perform_valid_action(self, form):
        self.perform_ticket_update(self.object.ticket,
                                   'Charge Modified',
                                   "$%.2f" % float(form.cleaned_data['cost']) + " - " + form.cleaned_data['item'])


class TicketMarkPaid(TicketActionBaseHandler):
    form_class = forms.TicketPaidForm
    permission_required = 'ticket.manage_ticket'

    def perform_invalid_action(self, form):
        messages.error(self.request, _('Error marking charge paid.'))

    def perform_valid_action(self, form):
        charges = TicketCharge.objects.filter(ticket=self.object)

        for charge in charges:
            if (charge.reconciled is True):
                continue

            date = datetime.now()

            if (form.data['paid_status'] == 'paid'):
                charge.reconciled = True
                charge.reconciled_date = date

            charge.paid_status = form.data['paid_status']
            charge.save()

        self.perform_ticket_update(self.object, 'Charge Modified', 'Charges marked as ' + form.data['paid_status'] + '. Comment: ' + form.data['comment'])

    def form_valid(self, form):
        self.perform_valid_action(form)

        return HttpResponseRedirect(reverse('ticket_details', kwargs={"ticket_id": self.object.pk}))


class TicketAdminSettingsHandler(TicketUpdateMixin, UpdateView):
    model = Ticket
    template_name = "modals/form_basic.jinja"
    form_class = forms.TicketAdminSettingsForm
    redirect = "ticket_list"
    permission_required = 'ticket.manage_ticket'

    """
    Administrator edits a ticket's properties (re-assignment, closing, etc)
    """

    def convert_users_to_ids(self, users):
        return [int(i.id) for i in users]

    def form_invalid(self, form):
        log.warning("Form errors: %s" % form.errors)
        messages.error(self.request, _('There was an error updating the ticket.'))
        return HttpResponseRedirect(reverse(self.redirect))

    def get(self, request, pk, redirect, status='success'):
        super(TicketAdminSettingsHandler, self).get(self, request)
        self.redirect = redirect

        t = render_to_string('modals/form_basic.jinja', self.get_context_data())
        return JsonResponse({'status': status, 'html': t})

    def get_context_data(self, **kwargs):
        context = super(TicketAdminSettingsHandler, self).get_context_data(**kwargs)
        context['csrf'] = get_token(self.request)
        context['form_action'] = reverse_lazy('ticket_admin_settings', kwargs={'pk': self.object.id, 'redirect': self.redirect})
        context['form'] = self.get_form(self.form_class)
        context['form'].fields['redirect'].initial = self.redirect
        return context

    def get_success_url(self):
        try:
            response = reverse_lazy(self.redirect)
            return response
        except Exception as ex:
            log.exception(ex)

        return reverse_lazy(self.redirect, kwargs={
            'ticket_id': self.object.id
        })


class TicketUpdateRemoveHandler(TicketActionBaseHandler):
    # it should be noted that while the intent of this handler
    # is to eventually cater to removing any ticket updates that
    # would be neccesary to remove, right now the assumption is
    # just for comments - 2014.03.22
    model = TicketUpdate
    form_class = forms.TicketEmptyForm
    ticket = None
    permission_required = 'ticket.manage_ticket'

    def get_ticket(self):
        self.ticket = Ticket.objects.get(pk=self.object.ticket_id)

    def form_invalid(self, form):
        self.get_ticket()
        self.perform_invalid_action(form)
        return HttpResponseRedirect(reverse('ticket_details', kwargs={
            "ticket_id": self.ticket.id
        }))

    def form_valid(self, form):
        self.get_ticket()
        self.perform_valid_action(form)
        super(TicketUpdateRemoveHandler, self).form_valid(form)
        return HttpResponseRedirect(reverse('ticket_details', kwargs={
            "ticket_id": self.ticket.id
        }))

    def perform_invalid_action(self, form):
        messages.error(self.request, _('There was an error deleting the comment.'))

    def perform_valid_action(self, form):
        self.success_messages = [_('The comment was successfully deleted.')]
        self.object.is_removed = True
        self.object.save()
        return super(TicketUpdateRemoveHandler, self).perform_valid_action(form)

    def __init__(self, *args, **kwargs):
        super(TicketUpdateRemoveHandler, self).__init__(*args, **kwargs)


class TicketDetail(TemplateView, PermissionRequiredMixin):
    template_name = "tickets/request_details.jinja"
    permission_required = 'ticket.view_ticket'

    """
    View for the requester of a ticket to view what is currently going on,
    and provide feedback / close the request / etc
    """
    def get_object(self):
        return Ticket.objects.get(id=self.kwargs["ticket_id"])

    def dispatch(self, request, **kwargs):
        if not self.has_permission():
            return self.handle_no_permission()
        self.ticket = self.get_object()
        if hasattr(self.ticket, "personticket"):
            self.ticket = self.ticket.personticket
        elif hasattr(self.ticket, "companyticket"):
            self.ticket = self.ticket.companyticket
        elif hasattr(self.ticket, "otherticket"):
            self.ticket = self.ticket.otherticket
        else:
            raise ValueError("Unknown ticket type")

        if not self.ticket:
            return self.abort(404)

        self.form = forms.CommentForm()
        return super(TicketDetail, self).dispatch(request)

    def get_context_data(self):
        ticket_updates = (TicketUpdate.objects
                          .filter(ticket=self.ticket, is_removed=False)
                          .order_by("created"))

        charges = (TicketCharge.objects.filter(ticket=self.ticket)
                   .order_by("created"))

        outstanding = TicketCharge.objects.filter(ticket=self.ticket,
                                                  reconciled=False)
        outstanding = sum([x.cost for x in outstanding])

        return {
            'ticket': self.ticket,
            'ticket_updates': ticket_updates,
            'charges': charges,
            'charges_outstanding': outstanding,
            'ticket_update_form': self.form,
            'cancel_form': forms.TicketEmptyForm(),
            'mark_paid_form': forms.TicketPaidForm(),
            'close_form': forms.TicketEmptyForm(),
            'open_form': forms.TicketCancelForm(),
            'flag_form': forms.RequestFlagForm(),
            'attachments': self.ticket.attachments.all(),
            'charge_form': forms.RequestChargeForm(),
            'ticket_detail_view': True
        }

    # FIXME: AJAXize!
    def post(self, request):
        form = forms.CommentForm(self.request.POST)

        if not form.is_valid():
            return self.get(request)

        comment = form.save(commit=False)
        comment.ticket = self.ticket
        comment.author = request.user
        comment.save()

        return HttpResponseRedirect(reverse('ticket_details', kwargs={
            "ticket_id": self.ticket.id
        }))


class TicketList(PrettyPaginatorMixin, CSVorJSONResponseMixin, TemplateView):
    template_name = "tickets/request_list.jinja"
    page_name = ""
    ticket_list_name = ""
    tickets = []
    page_number = 1
    page_size = 50
    page_buttons = 5
    page_buttons_padding = 2
    paginator = None
    url_name = 'ticket_list'
    url_args = {}
    CONTEXT_ITEMS_KEY = "tickets"
    CONTEXT_TITLE_KEY = "page_name"

    def get_context_data(self, **kwargs):
        self.kwargs = kwargs
        self.filter_terms = self.request.GET.get("filter", '')
        self.start_date = self.request.GET.get("start_date", '')
        self.end_date = self.request.GET.get("end_date", '')
        self.page_number = int(self.request.GET.get("page", 1))

        paged_tickets = self.get_paged_tickets(self.page_number)
        paginator = self.create_pretty_pagination_object(self.paginator,
                                                         self.page_number,
                                                         self.page_buttons,
                                                         self.page_buttons_padding,
                                                         self.url_name,
                                                         self.url_args),
        context = {
            'page_name': self.page_name,
            'ticket_list_name': self.ticket_list_name,
            'tickets': paged_tickets,
            'page_obj': paged_tickets,
            'paginator': self.paginator,
            'paginator_object': paginator,
            'page_number': self.page_number,
            'ticket_figures': self.get_ticket_list_figures(),
            'filter_terms': self.filter_terms,
            'start_date': self.start_date,
            'end_date': self.end_date,
            'possible_assignees': get_user_model().objects.filter(Q(is_superuser=True) |
                                                                  Q(is_staff=True))
        }
        return context

    def get_ticket_list_figures(self):
        ticket_figures = {
            'all_open': TicketListAllOpen().get_ticket_set(self.request.user).count(),
            'all_closed': TicketListAllClosed().get_ticket_set(self.request.user).count(),
            'my_open': TicketListMyOpen().get_ticket_set(self.request.user).count(),
            'my_closed': TicketListMyClosed().get_ticket_set(self.request.user).count(),
            'my_assigned': TicketListMyAssigned().get_ticket_set(self.request.user).count(),
            'my_assigned_closed': TicketListMyAssignedClosed().get_ticket_set(self.request.user).count(),
            'public': TicketListPublic().get_ticket_set(self.request.user).count(),
            'public_closed': TicketListPublicClosed().get_ticket_set(self.request.user).count(),
            'unassigned': TicketListUnassigned().get_ticket_set(self.request.user).count(),
            'upcoming_deadline': TicketListUpcomingDeadline().get_ticket_set(self.request.user).count(),
            'outstanding_charges': AdminOustandingChargesList().get_charges_set().count()
        }

        return ticket_figures

    def get_paged_tickets(self, page_number):
        self.set_paginator_object()

        try:
            paged_tickets = self.paginator.page(page_number)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            paged_tickets = self.paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            paged_tickets = self.paginator.page(self.paginator.num_pages)

        return paged_tickets

    def set_paginator_object(self):
        ticket_set = self.get_ticket_set(self.request.user)
        if self.filter_terms:
            ticket_set = ticket_set.filter(Q(requester__email__icontains=self.filter_terms)
                                         | Q(requester__first_name__icontains=self.filter_terms)
                                         | Q(requester__last_name__icontains=self.filter_terms)
                                         | Q(personticket__name__icontains=self.filter_terms)
                                         | Q(personticket__aliases__icontains=self.filter_terms)
                                         | Q(personticket__background__icontains=self.filter_terms)
                                         | Q(companyticket__name__icontains=self.filter_terms)
                                         | Q(companyticket__connections__icontains=self.filter_terms)
                                         | Q(companyticket__background__icontains=self.filter_terms)
                                         | Q(otherticket__question__icontains=self.filter_terms)
                                         )
        if self.start_date:
            ticket_set = ticket_set.filter(created__gte=self.start_date)

        if self.end_date:
            ticket_set = ticket_set.filter(created__lte=self.end_date)

        self.paginator = Paginator(ticket_set, self.page_size)

    def get_ticket_set(self, user):
        return self.tickets

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(TicketList, self).dispatch(*args, **kwargs)


class TicketListAllOpen(TicketList):
    page_name = "All Requests"
    ticket_list_name = "All Open Requests"
    url_name = 'ticket_all_open_list'

    def get_ticket_set(self, user):
        return Ticket.objects.filter(
            ~Q(status='closed')&~Q(status='cancelled')).order_by(
            "-created")


class TicketListAllClosed(TicketList):
    page_name = "All Requests"
    ticket_list_name = "All Closed Requests"
    url_name = 'ticket_all_closed_list'

    def get_ticket_set(self, user):
        return Ticket.objects.filter(
            Q(status='closed')).order_by("-created")


class TicketListMyOpen(TicketList):
    page_name = "My Requests"
    ticket_list_name = "My Open Requests"

    def get_ticket_set(self, user):
        return Ticket.objects.filter(
            requester=user).filter(
            ~Q(status='closed') & ~Q(status='cancelled')).order_by(
            "-created")


class TicketListMyClosed(TicketList):
    page_name = "My Requests"
    ticket_list_name = "My Closed Requests"

    def get_ticket_set(self, user):
        return Ticket.objects.filter(
            requester=user).filter(
            Q(status='closed')).order_by(
            "-created")


class TicketListMyAssigned(TicketList):
    page_name = "My Assignments"
    ticket_list_name = "Open Assignments"

    def get_ticket_set(self, user):
        return Ticket.objects.filter(responders__in=[user]).filter(
            ~Q(status='closed')&~Q(status='cancelled')).order_by(
            "-created")


class TicketListMyAssignedClosed(TicketList):
    page_name = "My Assignments"
    ticket_list_name = "Closed Assignments"

    def get_ticket_set(self, user):
        return Ticket.objects.filter(responders__in=[user]).filter(
            Q(status='closed')).order_by(
            "-created")


class TicketListPublic(TicketList):
    page_name = "Public Requests"
    ticket_list_name = "Open Public Requests"

    def get_ticket_set(self, user):
        return (Ticket.objects
                      .filter(is_public=True)
                      .exclude(status='closed')
                      .exclude(status='cancelled')
                      .order_by("-created")
                )


class TicketListPublicClosed(TicketList):
    page_name = "Pubic Requests"
    ticket_list_name = "Closed Public Requests"

    def get_ticket_set(self, user):
        return Ticket.objects.filter(
            is_public=True).filter(status='closed').order_by("-created")


class TicketListUnassigned(TicketList):
    page_name = "Unassigned Requests"
    ticket_list_name = "Unassigned Requests"
    url_name = 'ticket_unassigned_list'

    def get_ticket_set(self, user):
        return (Ticket.objects
                      .exclude(status='closed')
                      .exclude(status='cancelled')
                      .annotate(responder_count=Count('responders'))
                      .filter(responder_count=0)
                      .order_by("-created"))


class TicketListUpcomingDeadline(TicketList):
    page_name = "Upcoming Deadline Requests"
    ticket_list_name = "Requests with deadlines in the 30 days"
    url_name = 'ticket_deadline_list'

    def get_ticket_set(self, user):
        filter_date = datetime.now() + timedelta(days=30)

        return Ticket.objects.filter(
            Q(deadline__isnull=False) & Q(deadline__lte=filter_date)).filter(
            ~Q(status='closed')).order_by(
            "-created")


class TicketListUser(TicketList):
    url_name = 'ticket_user_list'

    def get_ticket_set(self, user):
        uid = self.kwargs.get("user_id")
        try:
            u = Profile.objects.get(id=uid)
        except:
            raise Http404
        self.page_name = "%s's tickets" % (u)
        self.ticket_list_name = "All tickets created by %s" % (u)
        return Ticket.objects.filter(requester=u).order_by("-created")


class TicketListCountry(TicketList):
    url_name = 'ticket_country_list'

    def get_ticket_set(self, user):
        from core.countries import COUNTRIES
        country = self.kwargs.get("country")
        u = dict(COUNTRIES)[country]
        self.page_name = "Tickets referring to companies in %s" % (u)
        self.ticket_list_name = "All tickets referring to country %s" % (u)
        return CompanyTicket.objects.filter(country=country).order_by("-created")


class TicketCountries(TemplateView):
    template_name = "tickets/countries.jinja"
    url_name = 'ticket_countries'

    def get_context_data(self):
        from core.countries import COUNTRIES
        from django.db.models import Count
        qs = CompanyTicket.objects.values('country').annotate(cnt_total=Count('country')).order_by('country')
        return {
            'countries': qs,
            'countrynames': dict(COUNTRIES)
        }


class TicketRequest(PermissionRequiredMixin, TemplateView):
    template_name = "tickets/request.jinja"
    permission_required = 'ticket.add_ticket'

    # runs when django forms clean the data but before django saves the object

    """ Some registered user submits a ticket for response by a responder. """
    def dispatch(self, *args, **kwargs):
        if self.request.method == 'POST':
            self.ticket_type_form = forms.TicketTypeForm(self.request.POST,
                                                         prefix='ticket_type')

            self.forms = {
                'ticket_type_form': self.ticket_type_form,
                'person_ownership_form': forms.PersonTicketForm(
                    self.request.POST,
                    prefix='person'),
                'company_ownership_form': forms.CompanyTicketForm(
                    self.request.POST,
                    prefix='company'),
                'other_form': forms.OtherTicketForm(
                    self.request.POST,
                    prefix='other')
            }
        else:
            self.forms = {
                'ticket_type_form': forms.TicketTypeForm(prefix='ticket_type'),
                'person_ownership_form': forms.PersonTicketForm(prefix='person'),
                'company_ownership_form': forms.CompanyTicketForm(prefix='company'),
                'other_form': forms.OtherTicketForm(prefix='other'),
            }
        return super(TicketRequest, self).dispatch(self.request)

    def get_context_data(self, ticket_id=None):
        ctx = {
            'ticket': None
        }
        ctx.update(self.forms)
        return ctx

    def post(self, ticket_id=None):
        if not self.forms["ticket_type_form"].is_valid():
            print self.forms["ticket_type_form"].errors.as_data()
            # self.add_message("Error")
            return

        ticket_type_form = self.forms["ticket_type_form"]
        ticket_type = ticket_type_form.cleaned_data["ticket_type"]
        form = self.forms[ticket_type + "_form"]

        if not form.is_valid():
            # self.add_message(_("Error: Form was not valid"))
            log.error('Invalid ticket creation form.')
            return self.get(None)

        ticket = form.save(commit=False)
        ticket.requester = self.request.user
        ticket.save()
        ticket.requester.notifications_subscribe('id:ticket:ticket:%d:update' % ticket.id)
        messages.success(self.request, _('Ticket successfully created.'))
        return HttpResponseRedirect(reverse('ticket_details', kwargs={
            "ticket_id": ticket.id
        }))


class TicketUserFeesOverview(PermissionRequiredMixin, CSVorJSONResponseMixin,
                             TemplateView):
    template_name = 'tickets/ticket_user_fees_overview.jinja'
    permission_required = 'ticket.report_ticket'
    CONTEXT_ITEMS_KEY = "users"

    def get_context_data(self):
        q = get_user_model().objects
        q = q.annotate(payment_count=Count('ticketcharge'))
        q = q.annotate(payment_total=Sum('ticketcharge__cost'))
        q = q.filter(payment_count__gt=0)
        return {
            "title": "User Fees",
            "users": q
        }


class TicketNetworkFeesOverview(PermissionRequiredMixin, CSVorJSONResponseMixin,
                                TemplateView):
    template_name = 'tickets/ticket_network_fees_overview.jinja'
    permission_required = 'ticket.report_ticket'
    CONTEXT_ITEMS_KEY = "networks"

    def get_context_data(self):
        return {
            "title": "Network Fees",
            "networks": Network.objects.all(),
        }


class TicketBudgetFeesOverview(PermissionRequiredMixin, CSVorJSONResponseMixin,
                               TemplateView):
    template_name = 'tickets/ticket_budget_fees_overview.jinja'
    permission_required = 'ticket.report_ticket'
    CONTEXT_ITEMS_KEY = "budgets"

    def get_context_data(self):
        return {
            "title": "Budget Fees",
            "budgets": Budget.objects.all(),
        }


class TicketResolutionWorkload(PermissionRequiredMixin, TemplateView):
    template_name = 'tickets/ticket_resolution_workload.jinja'
    permission_required = 'ticket.report_ticket'

    def get_context_data(self):
        researchers = get_user_model().objects.filter(
            Q(is_staff=True) | Q(is_superuser=True)
        )
        sort = self.request.GET.get("sort", "role")
        if sort == "role":
            researchers = researchers.order_by("-is_superuser", "-is_staff")
        return {
            "researchers": researchers
        }


class TicketResolutionTime(PermissionRequiredMixin, TemplateView):
    template_name = 'tickets/ticket_resolution_time.jinja'
    permission_required = 'ticket.report_ticket'

    def get_context_data(self):
        tickets = Ticket.objects.filter(status="closed")[:100]
        times = [x.resolution_time() for x in tickets]
        if len(times) == 0:
            average_timedelta = timedelta(0)
        else:
            average_timedelta = sum(times, timedelta(0)) / len(times)

        return {
            "averagetime": average_timedelta,
            "count": tickets.count()
        }


class TicketReport(CSVorJSONResponseMixin, PermissionRequiredMixin, TemplateView):
    template_name = 'tickets/ticket_report.jinja'
    CONTEXT_ITEMS_KEY = "tickets"
    permission_required = 'ticket.report_ticket'

    def get_context_data(self):
        start_date = self.request.GET.get('start_date', '')
        end_date = self.request.GET.get('end_date', '')

        tickets = Ticket.objects.all()
        if start_date:
            tickets = tickets.filter(created__gte=start_date)
        if end_date:
            tickets = tickets.filter(created__lte=end_date)

        return {
            'tickets': tickets,
            'title': 'Ticket report',
            'start_date': start_date,
            'end_date': end_date
        }


class TicketAttachmentDownload(TemplateView):

    def dispatch(self, request, pk=None):
        attachment = get_object_or_404(TicketAttachment, pk=pk)
        if not request.user.has_perm('ticket.view_ticket', attachment.ticket):
            raise PermissionDenied()
        log.debug('Serving: %s', attachment)
        resp = FileResponse(attachment.get_filehandle())
        resp['Content-Type'] = attachment.mimetype
        resp['Content-Disposition'] = 'filename=' + attachment.filename
        return resp


class TicketAttachmentUpload(TemplateView):

    def dispatch(self, request, *args, **kwargs):
        if request.method == 'POST':
            file_obj = request.FILES.get('file')
            ticket = Ticket.objects.get(pk=request.POST.get('ticket'))
            if not request.user.has_perm('ticket.view_ticket', ticket):
                raise PermissionDenied()

            if ticket is not None and file_obj is not None:
                # raise PermissionDenied()
                # or request.user not in ticket.actors()
                attachment = TicketAttachment.create_fh(ticket, request.user,
                                                        file_obj)
                log.debug('File created: %r', attachment)
        return HttpResponseRedirect(reverse('ticket_details', kwargs={
            "ticket_id": ticket.id
        }))
