# from app.auth import role_in
from id.models import Company, Person, Location
from django.views.generic import TemplateView
from id.mixins import JSONResponseMixin
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


class ValidateCompany(BaseValidator):
    # FIXME: Auth   @role_in('staff', 'admin')
    def post(self):
        # only care that name is valid.
        matching = Company.objects.filter(
            name=self.request.POST['name'])

        if self.remove_validatee(matching):
            self.respond('invalid', _("This may be a duplicate"))
        else:
            self.respond('valid', _("No duplicates detected"))


class ValidatePerson(BaseValidator):

    # FIXME: Auth   @role_in('staff', 'admin')
    def post(self):
        # first_name, last_name
        matching = Person.objects.filter(
            first_name=self.request.POST['first_name'],
            last_name=self.request.POST['last_name'])

        if self.remove_validatee(matching):
            self.respond('invalid',
                         _("First and last name match another person"))
        else:
            self.respond('valid', _("No duplicates detected"))


class ValidateLocation(BaseValidator):
    # FIXME: Auth   @role_in('staff', 'admin')
    def get_context_data(self):
        # only name
        matching = Location.objects.filter(name=self.request.POST['name'])

        if self.remove_validatee(matching):
            return self.respond('invalid', _("This may be a duplicate"))
        else:
            return self.respond('valid', _("No duplicates detected"))
