from django.contrib import messages
from django.core.urlresolvers import reverse, reverse_lazy
from django.http import JsonResponse
from django.utils.translation import ugettext_lazy as _

class TicketAjaxResponseMixin(object):

    def form_invalid(self, form):
        response = super(TicketAjaxResponseMixin, self).form_invalid(form)
        if self.request.is_ajax():
            return JsonResponse(form.errors, status=400)
        else:
            return response

    def form_valid(self, form):
        response = super(TicketAjaxResponseMixin, self).form_valid(form)
        if self.request.is_ajax():
            data = {
                'message': unicode(_("Ticket successfully updated.")),
                'pk': self.object.pk
            }
            return JsonResponse(data)
        else:
            return response

class TicketUpdateMixin(object):

    def form_valid(self, form, form_messages=None):
        if form_messages is None:
            form_messages = [_("Ticket successfully saved.")]

        for i in form_messages:
            messages.success(self.request, i)

        return super(TicketUpdateMixin, self).form_valid(form)

    def form_invalid(self, form, messags=None):
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
