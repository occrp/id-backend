import json
from django.core.urlresolvers import reverse, reverse_lazy
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
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

from core.mixins import JSONResponseMixin
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


class TicketActionJoinHandler(TicketActionBaseHandler):
    form_class = forms.TicketEmptyForm

    def perform_invalid_action(self, form):
        messages.error(self.request, _('There was an error adding you to the ticket.'))

    def perform_valid_action(self, form):
        ticket = self.object

        self.transition_ticket_from_new(ticket)

        if self.request.user.profile.is_staff or self.request.user.profile.is_admin:
            ticket.responders.add(self.request.user)
            self.success_messages = [_('You have successfully been added to the ticket.')]
            self.perform_ticket_update(ticket, 'Responder Joined', self.request.user.profile.display_name + unicode(_(' has joined the ticket')))
            return super(TicketActionJoinHandler, self).perform_valid_action(form)

        elif self.request.user.profile.is_volunteer:
            ticket.volunteers.add(self.request.user)
            self.success_messages = [_('You have successfully been added to the ticket.')]
            self.perform_ticket_update(ticket, 'Responder Joined', self.request.user.profile.display_name + unicode(_(' has joined the ticket')))
            return super(TicketActionJoinHandler, self).perform_valid_action(form)

        else:
            self.perform_invalid_action(form)

class TicketActionLeaveHandler(TicketActionBaseHandler):
    form_class = forms.TicketEmptyForm

    def perform_invalid_action(self, form):
        messages.error(self.request, _('There was an error removing you from the ticket.'))

    def perform_valid_action(self, form):
        ticket = self.object

        if self.request.user in ticket.responders.all():
            ticket.responders.remove(self.request.user)
            self.success_messages = [_('You have successfully been removed from the ticket.')]
            self.perform_ticket_update(ticket, 'Responder Left', self.request.user.profile.display_name + unicode(_(' has left the ticket')))
            return super(TicketActionLeaveHandler, self).perform_valid_action(form)
        elif self.request.user in ticket.volunteers.all():
            self.volunteers.remove(self.request.user)
            self.success_messages = [_('You have successfully been removed from the ticket.')]
            self.perform_ticket_update(ticket, 'Responder Left', self.request.user.profile.display_name + unicode(_(' has left the ticket')))
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


class TicketAdminSettingsHandler(TicketUpdateMixin, UpdateView):
    model = Ticket
    template_name = "modals/form_basic.jinja"
    form_class = forms.TicketAdminSettingsForm
    """
    Administrator edits a ticket's properties (re-assignment, closing, etc)
    """

    def convert_users_to_ids(self, users):
        return [int(i.id) for i in users]

    def form_invalid(self, form):
        messages.error(self.request, _('There was an error updating the ticket.'))
        return HttpResponseRedirect(reverse('ticket_list'))

    def form_valid(self, form):
        ticket = self.object
        form_responders = [int(i) for i in form.cleaned_data['responders']]
        form_volunteers = [int(i) for i in form.cleaned_data['volunteers']]

        current_responders = self.convert_users_to_ids(ticket.responders.all())
        current_volunteers = self.convert_users_to_ids(ticket.volunteers.all())

        if len(form_responders) > 0 or len(form_volunteers) > 0:
            self.transition_ticket_from_new(ticket)

        for i in form_responders:
            if i not in current_responders:
                u = User.objects.get(pk=i)
                self.perform_ticket_update(ticket, 'Responder Joined', u.profile.display_name + unicode(_(' has joined the ticket')))

        for i in form_volunteers:
            if i not in current_volunteers:
                u = User.objects.get(pk=i)
                self.perform_ticket_update(ticket, 'Responder Joined', u.profile.display_name + unicode(_(' has joined the ticket')))

        for i in current_responders:
            if i not in form_responders:
                u = User.objects.get(pk=i)
                self.perform_ticket_update(ticket, 'Responder Left', u.profile.display_name + unicode(_(' has left the ticket')))

        for i in current_volunteers:
            if i not in form_volunteers:
                u = User.objects.get(pk=i)
                self.perform_ticket_update(ticket, 'Responder Left', u.profile.display_name + unicode(_(' has left the ticket')))

        return super(TicketAdminSettingsHandler, self).form_valid(form)

    def get(self, request, pk, status='success'):
        super(TicketAdminSettingsHandler, self).get(self, request)

        t = render_to_string('modals/form_basic.jinja', self.get_context_data())
        return JsonResponse({'status': status, 'html': t})

    def get_context_data(self, **kwargs):
        context = super(TicketAdminSettingsHandler, self).get_context_data(**kwargs)
        context['csrf'] = get_token(self.request)
        context['form_action'] = reverse_lazy('ticket_admin_settings', kwargs={'pk': self.object.id})
        context['form'] = self.get_form(self.form_class)
        return context

    def get_success_url(self):
        return reverse_lazy('ticket_list')


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
        #     request.user.profile.is_admin or
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
            if self.request.user.profile.is_volunteer and self.ticket.is_public:
                can_join_leave = True

            if self.request.user.profile.is_volunteer and self.request.user in self.ticket.volunteers.all():
                can_join_leave = True

            if self.request.user.profile.is_admin or self.request.user.is_staff:
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

class TicketList(TemplateView, PodaciMixin):
    template_name = "tickets/request_list.jinja"

    """Display a list of requests which the currently logged in user has out in
    the wild."""

    #FIXME: Auth
    #@role_in('user', 'staff', 'admin', 'volunteer')
    def get_context_data(self):
        my_tickets_base = (Ticket.objects
                           .filter(requester=self.request.user)
                           .order_by('-created'))
        my_tickets = []
        for i in my_tickets_base:
            my_tickets.append(get_actual_ticket(i))
        open_tickets, closed_tickets = split_open_tickets(my_tickets)
        context = {
            'requests': open_tickets,
            'closed_requests': closed_tickets
        }
        return context

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(TicketList, self).dispatch(*args, **kwargs)

class TicketRequest(TemplateView, PodaciMixin):
    template_name = "tickets/request.jinja"

    # runs when django forms clean the data but before django saves the object
    def clean_family(self):
        data = self.cleaned_data['family']
        return data.strip()

    def clean_aliases(self):
        data = self.cleaned_data['aliases']
        return data.strip()

    def clean_connections(self):
        data = self.cleaned_data['connections']
        return data.strip()

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
        print "ticket post"
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
            "users": User.objects.annotate(payment_count=Count('ticketcharge')).annotate(payment_total=Sum('ticketcharge__cost')).filter(payment_count__gt=0)
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
