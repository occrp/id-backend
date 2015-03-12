from django.contrib import messages
from django.core.urlresolvers import reverse, reverse_lazy
from django.utils.translation import ugettext_lazy as _

class TicketUpdateMixin(object):

    def form_valid(self, form):
        messages.success(self.request, _("Ticket successfully saved."))
        return super(TicketUpdateMixin, self).form_valid(form)

    def form_invalid(self, form):
        messages.success(self.request, '')
        return super(TicketUpdateMixin, self).form_valid(form)

    def get_success_url(self):
        ticket = self.get_object()
        return reverse_lazy('ticket_details', kwargs={'ticket_id': ticket.id})


class TicketCreateMixin(object):

    def form_valid(self, form):
        messages.success(self.request, _('Ticket successfully created.'))
        return super(TicketUpdateMixin, self).form_valid(form)

    # # the ticket create view needs to be updated before we can use thisi effectively
    # def get_success_url(self):
    #     ticket = self.get_object()
    #     return reverse_lazy('ticket_details', kwargs={'ticket_id': ticket.id})
