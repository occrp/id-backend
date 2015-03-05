from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.views.generic import TemplateView
from django.utils.translation import ugettext_lazy as _

#  from core.mixins import MessageMixin

from ticket.models import Ticket
from ticket import forms

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

        print "ticket info"
        print " "
        print " "
        print ticket_type
        print form.errors.as_data()
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
