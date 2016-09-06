from __future__ import absolute_import
from django.contrib import messages
from django.core.urlresolvers import reverse_lazy
from django.http import JsonResponse
from django.utils.translation import ugettext_lazy as _
from rules.contrib.views import PermissionRequiredMixin

from .models import TicketUpdate
from . import constants


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


class TicketUpdateMixin(PermissionRequiredMixin):
    redirect = "default"

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

        if self.redirect == "default":
            return reverse_lazy('ticket_details',
                                kwargs={'ticket_id': ticket.id})
        else:
            return reverse_lazy(self.redirect)

    def perform_ticket_update(self, ticket, update_type, comment):
        perform_ticket_update(ticket, update_type, comment, self.request.user)

    def transition_ticket_from_new(self, ticket):
        transition_ticket_from_new(ticket)


# stand alone
def perform_ticket_update(ticket, update_type, comment, user):
    ticket_update = TicketUpdate(ticket=ticket)
    ticket_update.author = user
    ticket_update.update_type = constants.get_choice(update_type, constants.TICKET_UPDATE_TYPES)
    ticket_update.comment = comment
    ticket_update.save()


# stand alone
def transition_ticket_from_new(ticket):
    if ticket.status == constants.get_choice('New', constants.TICKET_STATUS):
        ticket.status = constants.get_choice('In Progress', constants.TICKET_STATUS)
        ticket.save()


class TicketCreateMixin(object):

    def form_valid(self, form):
        messages.success(self.request, _('Ticket successfully created.'))
        return super(TicketUpdateMixin, self).form_valid(form)

    # # the ticket create view needs to be updated before we can use thisi effectively
    # def get_success_url(self):
    #     ticket = self.get_object()
    #     return reverse_lazy('ticket_details', kwargs={'ticket_id': ticket.id})
