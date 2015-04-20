# from app.auth import role_in
from django.views.generic import TemplateView
from core.mixins import JSONResponseMixin
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ugettext as _nl

# Hint: JSON Serialization requires non-lazy gettext!

class BaseValidator(JSONResponseMixin, TemplateView):
    def respond(self, status, message):
        return {
            'status': status,
            'message': message
        }

    def remove_validatee(self, objects):
        return [o for o in objects
                if o.key.urlsafe() != self.request.POST['validation_key']]

