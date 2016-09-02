from django.views.generic import TemplateView
from django.utils.translation import ugettext as _nl

from core.mixins import JSONResponseMixin


class BaseValidator(JSONResponseMixin, TemplateView):
    def respond(self, status, message):
        return {
            'status': status,
            'message': message
        }

    def remove_validatee(self, objects):
        return [o for o in objects
                if o.key.urlsafe() != self.request.POST['validation_key']]


class ValidateTicketRequest(BaseValidator):
    """Validate requests by counting the word length of their text areas."""

    fields = {
        'person': ['summary', 'background', 'biography', 'business_activities',
                   'initial_information'],
        'company': ['summary', 'background', 'sources', 'story'],
        'other': ['summary', 'question']
    }
    type_field = 'ticket_type-ticket_type'
    min_word_count = 100

    # @role_in('user', 'staff', 'admin')
    def get_context_data(self):
        ticket_type = self.request.POST.get(self.type_field, None)
        if not ticket_type:
            return self.respond('error', _nl("No data provided"))
        if ticket_type != "other":
            ticket_type = ticket_type[:-10]  # FIXME: This is stupid

        word_count = 0
        for field in self.fields[ticket_type]:
            val = self.request.POST.get("%s-%s" % (ticket_type, field))
            if val:
                word_count += len(val.split(' '))

        if word_count < self.min_word_count:
            return self.respond(
                'invalid',
                _nl("Your request may not be answered, as you have not "
                    "provided much background. Please add more details."))

        msg = _nl("Your request is of an appropriate length.")
        return self.respond('valid', msg)
