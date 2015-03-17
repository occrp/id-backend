from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.contrib import messages
from django.core.urlresolvers import reverse, reverse_lazy
from django.views.generic import TemplateView, UpdateView

from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _

from core.mixins import JSONResponseMixin

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

# class TicketActionBaseHandler(JSONResponseMixin, TemplateView):
#     """
#     Base class for actions such as Cancel / Close / Etc from fragments to
#     inherit from
#     """

#     form_class = None

#     #FIXME: Auth
#     #@role_in('user', 'staff', 'admin', 'volunteer')
#     def get_context_data(self, ticket_id=None):
#         self.response.headers.add_header("Access-Control-Allow-Origin", "*")
#         ticket = Ticket.get_by_id(int(ticket_id))
#         form = self.form_class(self.request.POST)
#         not_allowed = not self.user_can(ticket)
#         if form.validate() and not not_allowed:
#             # save new update & add message
#             self.form_valid(ticket, form)
#         else:
#             t = self.render_template('modals/form_basic.jinja', form=form,
#                                      not_allowed=not_allowed)
#             self.render_json_response({'status': 'error', 'html': t})

class TicketActionBaseHandler(TicketUpdateMixin, UpdateView):
    model = Ticket
    form_class = forms.TicketCancelForm

    def perform_invalid_action(self, form):
        return

    def perform_valid_action(self, form):
        return

    def perform_ticket_update(self, ticket, update_type, comment):
        ticket_update = TicketUpdate(ticket=ticket)
        ticket_update.author = self.request.user
        ticket_update.update_type = constants.get_choice(update_type, constants.TICKET_UPDATE_TYPES)
        ticket_update.comment = comment
        ticket_update.save()

    def form_invalid(self, form):
        self.perform_invalid_action(form)
        return HttpResponseRedirect(reverse('ticket_details', kwargs={"ticket_id": self.object.id}))
        #return super(TicketActionBaseHandler, self).form_invalid(form)

    def form_valid(self, form):
        self.perform_valid_action(form)
        return super(TicketActionBaseHandler, self).form_valid(form)

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

    def perform_invalid_action(self, form):
        return

    def perform_valid_action(self, form):
        ticket = self.object

        if self.request.user.profile.is_staff or self.request.user.profile.is_admin:
            ticket.responders.add(self.request.user)
        elif self.request.user.profile.is_volunteer:
            ticket.volunteers.add(self.request.user)
        else:
            pass

        return super(TicketActionCancelHandler, self).perform_valid_action(form)

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
                          .filter(ticket=self.ticket)
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
