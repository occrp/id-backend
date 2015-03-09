from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.core.urlresolvers import reverse
from django.views.generic import TemplateView

from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _

from ticket.utils import *

#  from core.mixins import MessageMixin

from ticket.models import Ticket, PersonTicket, CompanyTicket, OtherTicket, TicketUpdate, TicketCharge
from ticket import forms

class TicketDetail(TemplateView):
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

        if not self.ticket.is_public and not (
            request.user.profile.is_admin or
            request.user == self.ticket.requester or
            request.user in self.ticket.responders.objects.all() or
            request.user in self.ticket.volunteers.objects.all()):
                return self.abort(401)

        self.form = forms.CommentForm()
        #form.author.data = request.user.id
        # form.ticket.data = ticket.id
        return super(TicketDetail, self).dispatch(request)

    def get_context_data(self):
        ticket_updates = (TicketUpdate.objects
                          .filter(ticket=self.ticket)
                          .order_by("created"))

        charges = (TicketCharge.objects.filter(ticket=self.ticket)
                   .order_by("created"))

        outstanding = TicketCharge.outstanding_charges(
            charges, pluck="cost")

        return {
            'ticket': self.ticket,
            'ticket_updates': ticket_updates,
            'charges': charges,
            'charges_outstanding': sum(outstanding),
            'ticket_update_form': self.form,
            'cancel_form': forms.RequestCancelForm(),
            'mark_paid_form': forms.TicketPaidForm(),
            'close_form': forms.RequestCancelForm(),
            're_open_form': forms.RequestCancelForm(),
            'flag_form': forms.RequestFlagForm(),
            'file_upload_form': forms.DirectUploadForm(initial={
                "key":self.ticket.id,
                "redirect_to":'/request/%s/details' % self.ticket.id}),
            'charge_form': forms.RequestChargeForm()
        }

    #FIXME: AJAXize!
    #FIXME: Auth
    #@role_in('user', 'staff', 'admin', 'volunteer')
    def post(self, request):
        print self.ticket
        form = forms.CommentForm(self.request.POST)

        if not form.is_valid():
            print "FORM WAS INVALID!!!"
            return self.get(request)

        comment = form.save(commit=False)
        print comment
        comment.ticket = self.ticket
        comment.author = request.user
        print "YAAY SAVING!!"
        comment.save()
        return HttpResponseRedirect(reverse('request_details', kwargs={ "ticket_id":self.ticket.id}))

class TicketList(TemplateView):
    template_name = "tickets/request_list.jinja"

    """Display a list of requests which the currently logged in user has out in
    the wild."""

    #FIXME: Auth
    #@role_in('user', 'staff', 'admin', 'volunteer')
    def get_context_data(self):
        print "get ticket list asfda';fda"
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

class TicketRequest(TemplateView):
    template_name = "tickets/request.jinja"

    """ Some registered user submits a ticket for response by a responder. """
    def dispatch(self, request):
        self.ticket = None
        if request.method == 'POST':
            self.ticket_type_form = forms.TicketTypeForm(self.request.POST,
                                                         prefix='ticket_type')

            if 'ticket_id' in self.kwargs:
                ticket_id = int(self.kwargs['ticket_id'])
                self.ticket = models.Ticket.objects.get_by_id(ticket_id)
                self.ticket_type_form.ticket_type.data = self.ticket.ticket_type

            self.forms = {
                'ticket_type_form': self.ticket_type_form,
                'person_ownership_form': forms.PersonTicketForm(
                    self.request.POST,
                    prefix='person',
                    instance=self.ticket),
                'company_ownership_form': forms.CompanyTicketForm(
                    self.request.POST,
                    prefix='company',
                    instance=self.ticket),
                'other_form': forms.OtherTicketForm(
                    self.request.POST,
                    prefix='other',
                    instance=self.ticket)
            }
        else:
            self.forms = {
                'ticket_type_form': forms.TicketTypeForm(prefix='ticket_type'),
                'person_ownership_form': forms.PersonTicketForm(prefix='person'),
                'company_ownership_form': forms.CompanyTicketForm(prefix='company'),
                'other_form': forms.OtherTicketForm(prefix='other'),
            }
        return super(TicketRequest, self).dispatch(request)

    #FIXME: Auth
    #@role_in('user', 'staff', 'admin', 'volunteer',
    #         fail_redirect=('request_unauthorized',))  # Reversed by role_in
    def get_context_data(self, ticket_id=None):
        ctx = {
            'ticket': self.ticket
        }
        ctx.update(self.forms)
        return ctx

    #FIXME: Auth
    #@role_in('user', 'staff', 'admin', 'volunteer')
    def post(self, ticket_id=None):
        print "ticket post"
        if not self.forms["ticket_type_form"].is_valid():
            # self.add_message("Error")
            return

        ticket_type = self.forms["ticket_type_form"].cleaned_data["ticket_type"]
        form = self.forms[ticket_type+"_form"]

        if form is forms.PersonTicketForm:
            form.family = form.family.strip()
            form.aliases = form.aliases.strip()
        if form is forms.CompanyTicketForm:
            form.connections = form.connections.strip()

        print "ticket info"
        print " "
        print " "
        print ticket_type
        print form.errors.as_data()
        print form.connections
        print "end form"

        if not form.is_valid():
            # self.add_message(_("Error: Form was not valid"))
            print "FORM ERROR NOT VALID!!!"
            return self.get(None)

        ticket = form.save(commit=False)
        ticket.requester = self.request.user
        ticket.save()

        # if ticket_id:
        #     self.add_message(_('Ticket successfully saved.'))
        # else:
        #     self.add_message(_('Ticket successfully created.'))

        return HttpResponseRedirect(reverse('request_details', kwargs={"ticket_id": ticket.id}))
