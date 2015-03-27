import json
from datetime import datetime, timedelta

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.urlresolvers import reverse, reverse_lazy
from django.contrib import messages
from django.contrib.auth.decorators import login_required
#from django.contrib.auth.models import User
from django.contrib.auth import get_user_model # as per https://docs.djangoproject.com/en/dev/topics/auth/customizing/#referencing-the-user-model
from django.contrib import messages
from django.db.models import Count
from django.db.models import Q
import django.forms
from django.forms.utils import ErrorList
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.http import JsonResponse
from django.middleware.csrf import get_token
from django.template.loader import render_to_string
from django.template import RequestContext
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from django.views.generic import TemplateView, UpdateView

from django.db.models import Count, Sum

from core.mixins import JSONResponseMixin, PrettyPaginatorMixin
from core.utils import *

from ticket.utils import *
from ticket.mixins import *
from ticket.models import Ticket, PersonTicket, CompanyTicket, OtherTicket, TicketUpdate, TicketCharge
from ticket import forms
from ticket import constants

from podaci import PodaciMixin

class CompanyTicketUpdate(TicketUpdateMixin, UpdateView, PodaciMixin):
    model = CompanyTicket
    template_name = 'tickets/request.jinja'
    form_class = forms.CompanyTicketForm

    def get_context_data(self, **kwargs):
        context = super(CompanyTicketUpdate, self).get_context_data(**kwargs)
        context['ticket'] = self.get_object()
        context['company_ownership_form'] = context['form']
        return context

    def __init__(self, *args, **kwargs):
        super(CompanyTicketUpdate, self).__init__(*args, **kwargs)

class OtherTicketUpdate(TicketUpdateMixin, UpdateView, PodaciMixin):
    model = OtherTicket
    template_name = 'tickets/request.jinja'
    form_class = forms.OtherTicketForm

    def get_context_data(self, **kwargs):
        context = super(OtherTicketUpdate, self).get_context_data(**kwargs)
        context['ticket'] = self.get_object()
        context['other_form'] = context['form']
        return context

    def __init__(self, *args, **kwargs):
        super(OtherTicketUpdate, self).__init__(*args, **kwargs)

class PersonTicketUpdate(TicketUpdateMixin, UpdateView, PodaciMixin):
    model = PersonTicket
    template_name = 'tickets/request.jinja'
    form_class = forms.PersonTicketForm

    def get_context_data(self, **kwargs):
        context = super(PersonTicketUpdate, self).get_context_data(**kwargs)
        context['ticket'] = self.get_object()
        context['person_ownership_form'] = context['form']
        return context

    def __init__(self, *args, **kwargs):
        super(PersonTicketUpdate, self).__init__(*args, **kwargs)


class TicketActionBaseHandler(TicketUpdateMixin, UpdateView):
    model = Ticket
    form_class = forms.TicketCancelForm

    success_messages = None
    failure_messages = None
    force_invalid = False

    def perform_invalid_action(self, form):
        return

    def perform_valid_action(self, form):
        return

    def form_invalid(self, form):
        self.perform_invalid_action(form)
        return HttpResponseRedirect(reverse('ticket_details', kwargs={"ticket_id": self.object.id}))
        #return super(TicketActionBaseHandler, self).form_invalid(form)

    def form_valid(self, form):
        self.perform_valid_action(form)

        if self.force_invalid is True:
            return self.form_invalid(form)

        return super(TicketActionBaseHandler, self).form_valid(form, self.success_messages)

    def get_success_url(self):
        ticket = self.get_object()
        return reverse_lazy('ticket_details', kwargs={'ticket_id': ticket.id})

class TicketActionCancelHandler(TicketActionBaseHandler):

    def perform_invalid_action(self, form):
        messages.error(self.request, _('A reason must be supplied to cancel the ticket.'))

    def perform_valid_action(self, form):
        ticket = self.object
        ticket.status = constants.get_choice('Cancelled', constants.TICKET_STATUS)
        self.perform_ticket_update(ticket, 'Cancelled', form.cleaned_data['reason'])
        return super(TicketActionCancelHandler, self).perform_valid_action(form)

class TicketActionCloseHandler(TicketActionBaseHandler):

    def perform_invalid_action(self, form):
        messages.error(self.request, _('A reason must be supplied to close the ticket.'))

    def perform_valid_action(self, form):
        ticket = self.object
        ticket.status = constants.get_choice('Closed', constants.TICKET_STATUS)
        self.perform_ticket_update(ticket, 'Closed', form.cleaned_data['reason'])
        return super(TicketActionCloseHandler, self).perform_valid_action(form)


class TicketActionJoinHandler(TicketActionBaseHandler, PodaciMixin):
    form_class = forms.TicketEmptyForm

    def perform_invalid_action(self, form):
        messages.error(self.request, _('There was an error adding you to the ticket.'))

    def perform_valid_action(self, form):
        ticket = self.object

        self.podaci_setup()
        tag = self.fs.get_tag(ticket.tag_id)

        if self.request.userg.is_staff or self.request.user.profile.is_superuser:
            ticket.responders.add(self.request.user)
            self.success_messages = [_('You have successfully been added to the ticket.')]
            self.perform_ticket_update(ticket, 'Responder Joined', self.request.userg.display_name + unicode(_(' has joined the ticket')))
            self.transition_ticket_from_new(ticket)

            tag.add_user(self.request.user, True)

            return super(TicketActionJoinHandler, self).perform_valid_action(form)

        elif self.request.userg.is_volunteer:
            ticket.volunteers.add(self.request.user)
            self.success_messages = [_('You have successfully been added to the ticket.')]
            self.perform_ticket_update(ticket, 'Responder Joined', self.request.userg.display_name + unicode(_(' has joined the ticket')))
            self.transition_ticket_from_new(ticket)

            tag.add_user(self.request.user, True)

            return super(TicketActionJoinHandler, self).perform_valid_action(form)

        else:
            self.perform_invalid_action(form)

class TicketActionLeaveHandler(TicketActionBaseHandler, PodaciMixin):
    form_class = forms.TicketEmptyForm

    def perform_invalid_action(self, form):
        messages.error(self.request, _('There was an error removing you from the ticket.'))

    def perform_valid_action(self, form):
        ticket = self.object

        self.podaci_setup()
        tag = self.fs.get_tag(ticket.tag_id)

        if self.request.user in ticket.responders.all():
            ticket.responders.remove(self.request.user)
            self.success_messages = [_('You have successfully been removed from the ticket.')]
            self.perform_ticket_update(ticket, 'Responder Left', self.request.userg.display_name + unicode(_(' has left the ticket')))

            tag.remove_user(self.request.user)

            return super(TicketActionLeaveHandler, self).perform_valid_action(form)
        elif self.request.user in ticket.volunteers.all():
            self.volunteers.remove(self.request.user)
            self.success_messages = [_('You have successfully been removed from the ticket.')]
            self.perform_ticket_update(ticket, 'Responder Left', self.request.userg.display_name + unicode(_(' has left the ticket')))

            tag.remove_user(self.request.user)

            return super(TicketActionLeaveHandler, self).perform_valid_action(form)
        else:
            self.force_invalid = True


class TicketActionOpenHandler(TicketActionBaseHandler):

    def perform_invalid_action(self, form):
        messages.error(self.request, _('A reason must be supplied to (re)open the.'))

    def perform_valid_action(self, form):
        ticket = self.object

        if(ticket.volunteers.count() == 0 and ticket.responders.count() == 0):
            ticket.status = constants.get_choice('New', constants.TICKET_STATUS)
        else:
            ticket.status = constants.get_choice('In Progress', constants.TICKET_STATUS)

        self.perform_ticket_update(ticket, 'Opened', form.cleaned_data['reason'])

        return super(TicketActionOpenHandler, self).perform_valid_action(form)


class TicketAdminSettingsHandler(TicketUpdateMixin, UpdateView, PodaciMixin):
    model = Ticket
    template_name = "modals/form_basic.jinja"
    form_class = forms.TicketAdminSettingsForm
    redirect = "ticket_list"
    """
    Administrator edits a ticket's properties (re-assignment, closing, etc)
    """

    def convert_users_to_ids(self, users):
        return [int(i.id) for i in users]

    def form_invalid(self, form):
        messages.error(self.request, _('There was an error updating the ticket.'))
        return HttpResponseRedirect(reverse(self.redirect))

    def form_valid(self, form):
        ticket = self.object
        form_responders = [int(i) for i in form.cleaned_data['responders']]
        form_volunteers = [int(i) for i in form.cleaned_data['volunteers']]

        current_responders = self.convert_users_to_ids(ticket.responders.all())
        current_volunteers = self.convert_users_to_ids(ticket.volunteers.all())

        self.podaci_setup()
        tag = self.fs.get_tag(ticket.tag_id)

        if 'redirect' in self.request.POST:
            self.redirect = self.request.POST['redirect']

        if len(form_responders) > 0 or len(form_volunteers) > 0:
            self.transition_ticket_from_new(ticket)

        for i in form_responders:
            if i not in current_responders:
                u = get_user_model().objects.get(pk=i)
                tag.add_user(u, True)
                self.perform_ticket_update(ticket, 'Responder Joined', ug.display_name + unicode(_(' has joined the ticket')))

        for i in form_volunteers:
            if i not in current_volunteers:
                u = get_user_model().objects.get(pk=i)
                tag.add_user(u, True)
                self.perform_ticket_update(ticket, 'Responder Joined', ug.display_name + unicode(_(' has joined the ticket')))

        for i in current_responders:
            if i not in form_responders:
                u = get_user_model().objects.get(pk=i)
                tag.remove_user(u)
                self.perform_ticket_update(ticket, 'Responder Left', ug.display_name + unicode(_(' has left the ticket')))

        for i in current_volunteers:
            if i not in form_volunteers:
                u = get_user_model().objects.get(pk=i)
                tag.remove_user(u)
                self.perform_ticket_update(ticket, 'Responder Left', ug.display_name + unicode(_(' has left the ticket')))

        return super(TicketAdminSettingsHandler, self).form_valid(form)

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
        return reverse_lazy(self.redirect)


class TicketUpdateRemoveHandler(TicketActionBaseHandler):
    # it should be noted that while the intent of this handler
    # is to eventually cater to removing any ticket updates that
    # would be neccesary to remove, right now the assumption is
    # just for comments - 2014.03.22
    model = TicketUpdate
    form_class = forms.TicketEmptyForm
    ticket = None

    def get_ticket(self):
        self.ticket = Ticket.objects.get(pk=self.object.ticket_id)

    def form_invalid(self, form):
        self.get_ticket()
        self.perform_invalid_action(form)
        return HttpResponseRedirect(reverse('ticket_details', kwargs={"ticket_id": self.ticket.id}))

    def form_valid(self, form):
        self.get_ticket()
        self.perform_valid_action(form)
        super(TicketUpdateRemoveHandler, self).form_valid(form)
        return HttpResponseRedirect(reverse('ticket_details', kwargs={"ticket_id": self.ticket.id}))

    def perform_invalid_action(self, form):
        messages.error(self.request, _('There was an error deleting the comment.'))

    def perform_valid_action(self, form):
        self.success_messages = [_('The comment was successfully deleted.')]
        self.object.is_removed = True
        self.object.save()
        return super(TicketUpdateRemoveHandler, self).perform_valid_action(form)

    def __init__(self, *args, **kwargs):
        super(TicketUpdateRemoveHandler, self).__init__(*args, **kwargs)


class TicketDetail(TemplateView, PodaciMixin):
    template_name = "tickets/request_details.jinja"
    """
    View for the requester of a ticket to view what is currently going on,
    and provide feedback / close the request / etc
    """
    #FIXME: Auth
    #@role_in('user', 'staff', 'admin', 'volunteer')
    def dispatch(self, request, ticket_id=None):
        self.ticket = Ticket.objects.get(id=int(ticket_id))
        if hasattr(self.ticket, "personticket"):
            self.ticket = self.ticket.personticket
        elif hasattr(self.ticket, "companyticket"):
            self.ticket = self.ticket.companyticket
        elif hasattr(self.ticket, "otherticket"):
            self.ticket = self.ticket.otherticket
        else:
            print dir(self.ticket)
            raise ValueError("Unknown ticket type")

        if not self.ticket:
            return self.abort(404)

        # if not self.ticket.is_public and not (
        #     request.userg.is_superuser or
        #     request.user == self.ticket.requester or
        #     request.user in self.ticket.responders.all() or
        #     request.user in self.ticket.volunteers.all()):
        #         return self.abort(401)

        self.form = forms.CommentForm()
        #form.author.data = request.user.id
        # form.ticket.data = ticket.id
        return super(TicketDetail, self).dispatch(request)

    def get_context_data(self):
        ticket_updates = (TicketUpdate.objects
                          .filter(ticket=self.ticket, is_removed=False)
                          .order_by("-created"))

        charges = (TicketCharge.objects.filter(ticket=self.ticket)
                   .order_by("created"))

        outstanding = TicketCharge.outstanding_charges(
            charges, pluck="cost")

        self.podaci_setup()

        if self.ticket.tag_id == "":
            # Create Podaci tag for this ticket.
            tag_name = "Ticket %d" % (self.ticket.id)

            tag = self.fs.create_tag(tag_name)
            self.ticket.tag_id = tag.id
            self.ticket.save()
        else:
            tag = self.fs.get_tag(self.ticket.tag_id)

        can_join_leave = False
        if self.request.user != self.ticket.requester:
            if self.request.userg.is_volunteer and self.ticket.is_public:
                can_join_leave = True

            if self.request.userg.is_volunteer and self.request.user in self.ticket.volunteers.all():
                can_join_leave = True

            if self.request.userg.is_superuser or self.request.user.is_staff:
                can_join_leave = True

        return {
            'ticket': self.ticket,
            'ticket_updates': ticket_updates,
            'charges': charges,
            'charges_outstanding': sum(outstanding),
            'ticket_update_form': self.form,
            'cancel_form': forms.TicketCancelForm(),
            'mark_paid_form': forms.TicketPaidForm(),
            'close_form': forms.TicketCancelForm(),
            'open_form': forms.TicketCancelForm(),
            'flag_form': forms.RequestFlagForm(),
            'tag': tag,
            'result_files': tag.get_files()[1],
            'charge_form': forms.RequestChargeForm(),
            'ticket_detail_view': True,
            'can_join_leave': can_join_leave
        }

    #FIXME: AJAXize!
    #FIXME: Auth
    #@role_in('user', 'staff', 'admin', 'volunteer')
    def post(self, request):
        print self.ticket
        form = forms.CommentForm(self.request.POST)

        if not form.is_valid():
            return self.get(request)

        comment = form.save(commit=False)
        print comment
        comment.ticket = self.ticket
        comment.author = request.user
        comment.save()
        return HttpResponseRedirect(reverse('ticket_details', kwargs={ "ticket_id":self.ticket.id}))

class TicketList(PrettyPaginatorMixin, TemplateView, PodaciMixin):
    template_name = "tickets/request_list.jinja"
    page_name = ""
    ticket_list_name = ""
    tickets = []
    page_number = 1
    page_size = 10
    page_buttons = 5
    page_buttons_padding = 2
    paginator = None
    url_name = 'ticket_list'
    url_args = {}

    def get_context_data(self, **kwargs):
        if 'page' in kwargs:
            self.page_number = int(kwargs.pop('page'))
            if self.page_number is None:
                self.page_number = 1

        context = {
            'page_name': self.page_name,
            'ticket_list_name': self.ticket_list_name,
            'tickets': self.get_paged_tickets(self.page_number),
            'paginator_object': self.create_pretty_pagination_object(self.paginator,
                                                                     self.page_number,
                                                                     self.page_buttons,
                                                                     self.page_buttons_padding,
                                                                     self.url_name,
                                                                     self.url_args),
            'page_number': self.page_number
        }

        return context

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
        self.paginator = Paginator(self.get_ticket_set(), self.page_size)

    def get_ticket_set(self):
        return self.tickets

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(TicketList, self).dispatch(*args, **kwargs)


class TicketListAllOpen(TicketList):
    page_name = "All Requests"
    ticket_list_name = "All Open Requests"

    def get_ticket_set(self):
        return get_actual_tickets(Ticket.objects.filter(
            ~Q(status=constants.get_choice('Closed', constants.TICKET_STATUS))).order_by(
            "-created"))

class TicketListAllClosed(TicketList):
    page_name = "All Requests"
    ticket_list_name = "All Closed Requests"

    def get_ticket_set(self):
        return get_actual_tickets(Ticket.objects.filter(
            Q(status=constants.get_choice('Closed', constants.TICKET_STATUS))).order_by(
            "-created"))

class TicketListMyOpen(TicketList):
    page_name = "My Requests"
    ticket_list_name = "My Open Requests"

    def get_ticket_set(self):
        return get_actual_tickets(Ticket.objects.filter(
            requester=self.request.user).filter(
            ~Q(status=constants.get_choice('Closed', constants.TICKET_STATUS))).order_by(
            "-created"))

class TicketListMyClosed(TicketList):
    page_name = "My Requests"
    ticket_list_name = "My Closed Requests"

    def get_ticket_set(self):
        return get_actual_tickets(Ticket.objects.filter(
            requester=self.request.user).filter(
            Q(status=constants.get_choice('Closed', constants.TICKET_STATUS))).order_by(
            "-created"))

class TicketListMyAssigned(TicketList):
    page_name = "My Assignments"
    ticket_list_name = "Open Assignments"

    def get_ticket_set(self):
        return get_actual_tickets(Ticket.objects.filter(
            Q(responders__in=[self.request.user]) | Q(volunteers__in=[self.request.user])).filter(
            ~Q(status=constants.get_choice('Closed', constants.TICKET_STATUS))).order_by(
            "-created"))

class TicketListMyAssignedClosed(TicketList):
    page_name = "My Assignments"
    ticket_list_name = "Closed Assignments"

    def get_ticket_set(self):
        return get_actual_tickets(Ticket.objects.filter(
            Q(responders__in=[self.request.user]) | Q(volunteers__in=[self.request.user])).filter(
            Q(status=constants.get_choice('Closed', constants.TICKET_STATUS))).order_by(
            "-created"))


class TicketListPublic(TicketList):
    page_name = "Public Requests"
    ticket_list_name = "Open Public Requests"

    def get_ticket_set(self):
        return get_actual_tickets(Ticket.objects.filter(
            is_public=True).filter(
            ~Q(status=constants.get_choice('Closed', constants.TICKET_STATUS))).order_by(
            "-created"))

class TicketListPublicClosed(TicketList):
    page_name = "Pubic Requests"
    ticket_list_name = "Closed Public Requests"

    def get_ticket_set(self):
        return get_actual_tickets(Ticket.objects.filter(
            is_public=True).filter(
            Q(status=constants.get_choice('Closed', constants.TICKET_STATUS))).order_by(
            "-created"))


class TicketListUnassigned(TicketList):
    page_name = "Unassigned Requests"
    ticket_list_name = "Unassigned Requests"

    def get_ticket_set(self):
        return get_actual_tickets(Ticket.objects.annotate(
            volunteer_count=Count('volunteers')).annotate(
            responder_count=Count('responders')).filter(
            Q(volunteer_count=0) & Q(responder_count=0)).order_by(
            "-created"))


class TicketListUpcomingDeadline(TicketList):
    page_name = "Upcoming Deadline Requests"
    ticket_list_name = "Requests with deadlines in the 30 days"

    def get_ticket_set(self):
        filter_date = datetime.now() + timedelta(days=30)

        return get_actual_tickets(Ticket.objects.filter(
            Q(deadline__isnull=False) & Q(deadline__lte=filter_date)).filter(
            ~Q(status=constants.get_choice('Closed', constants.TICKET_STATUS))).order_by(
            "-created"))


class TicketRequest(TemplateView, PodaciMixin):
    template_name = "tickets/request.jinja"

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

    #FIXME: Auth
    #@role_in('user', 'staff', 'admin', 'volunteer',
    #         fail_redirect=('request_unauthorized',))  # Reversed by role_in
    def get_context_data(self, ticket_id=None):
        ctx = {
            'ticket': None
        }
        ctx.update(self.forms)
        return ctx

    #FIXME: Auth
    #@role_in('user', 'staff', 'admin', 'volunteer')
    def post(self, ticket_id=None):
        if not self.forms["ticket_type_form"].is_valid():
            print self.forms["ticket_type_form"].errors.as_data()
            # self.add_message("Error")
            return

        ticket_type = self.forms["ticket_type_form"].cleaned_data["ticket_type"]
        form = self.forms[ticket_type+"_form"]

        # print "ticket info"
        # print " "
        # print " "
        # print ticket_type
        # print form.errors.as_data()
        # print "end form"

        if not form.is_valid():
            # self.add_message(_("Error: Form was not valid"))
            print "FORM ERROR NOT VALID!!!"
            return self.get(None)

        ticket = form.save(commit=False)
        ticket.requester = self.request.user
        ticket.save()
        messages.success(self.request, _('Ticket successfully created.'))

        self.podaci_setup()

        # Create Podaci tag for this ticket.
        tag_name = "Ticket %d" % (ticket.id)
        tag = self.fs.create_tag(tag_name)
        # TODO: Put this tag in a nice root tag.
        ticket.tag_id = tag.id
        ticket.save()

        # if ticket_id:
        #     self.add_message(_('Ticket successfully saved.'))
        # else:
        #     self.add_message(_('Ticket successfully created.'))

        return HttpResponseRedirect(reverse('ticket_details', kwargs={"ticket_id": ticket.id}))


class TicketUserFeesOverview(TemplateView):
    template_name = 'tickets/ticket_user_fees_overview.jinja'

    def get_context_data(self):
        return {
            "users": get_user_model().objects.annotate(payment_count=Count('ticketcharge')).annotate(payment_total=Sum('ticketcharge__cost')).filter(payment_count__gt=0)
        }

class TicketNetworkFeesOverview(TemplateView):
    template_name = 'tickets/ticket_network_fees_overview.jinja'

    def get_context_data(self):
        return {
            "networks": Network.objects.all(),
        }

class TicketBudgetFeesOverview(TemplateView):
    template_name = 'tickets/ticket_budget_fees_overview.jinja'

    def get_context_data(self):
        return {
            "budgets": [],
        }
