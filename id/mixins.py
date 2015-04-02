import json
from django.db import models
from django.http import HttpResponse
from django.utils.translation import ugettext_lazy as _

from ticket.constants import *

class MessageMixin(object):
    def add_message(self, message, level='success'):
        # if isinstance(message, LazyProxy):
        #    message = unicode(message)
        print dir(self.request.session)
        if not hasattr(self, "messages"):
            self.messages = []
        self.messages.append((message, level))


class DisplayMixin(object):
    """
    Renders a field's value in a display-friendly way. Should only be mixed
    in with models. It really should be accessible from properties but
    I didn't want to subclass all ndb field types.
    """
    def get_display_value(self, property_name):
        prop = getattr(self, property_name)
        value = (prop._get_display_value(self)
                 if hasattr(prop, '_get_display_value')
                 else getattr(self, property_name))

        if isinstance(value, list):
            value = ', '.join(value)

        return value


class ModelDiffMixin(object):
    """
    Provide an API to determine what fields changed before a model is saved.
    """
    @property
    def diff(self):
        if self.is_new:
            return {'old': None, 'changed_properties': []}

        properties = [p for p in type(self)._properties if p != 'class']
        changed_properties = []
        old = self.key.get()
        new = self

        for prop in properties:
            d1_val = getattr(old, prop)
            d2_val = getattr(new, prop)
            if d1_val != d2_val:
                changed_properties.append(prop)
        return {'old': old, 'changed_properties': changed_properties}

    @property
    def is_new(self):
        return not bool(self.key)


class AddressMixin(object):
    address = models.CharField(max_length=70, verbose_name=_('Address'))
    city = models.CharField(max_length=50, verbose_name=_('City'))
    province = models.CharField(max_length=50, verbose_name=_('State/Province/Region'))
    postal_code = models.CharField(max_length=50, verbose_name=_('ZIP/Postal Code'))
    country = models.CharField(max_length=50, choices=COUNTRIES, verbose_name=_('Country'))


class UserDetailsGenericMixin(object):
    '''This (and the similar classes below)
    are used to share fields between User Profiles
    and account requests. When an account request is approved,
    the UserProfile is updated with the data supplied by the user

    note that AccountRequests are polymorphic -- some fields are only declared
    in the relevant subclass. However, User Profiles are not polymorphic;
    each UserProfile contains all fields, relevant or not
    '''

    first_name = models.CharField(max_length=50, verbose_name=_('First Name'))
    last_name = models.CharField(max_length=50, verbose_name=_('Last Name'))
    phone_number = models.CharField(max_length=50, verbose_name=_('Phone Number'))
    organization_membership = models.CharField(max_length=50, 
        choices=ORGANIZATION_TYPES,
        verbose_name=_('Organization Membership'))
    notes = models.TextField(
        verbose_name=_('Anything else you would like to tell us'))

    class Meta:
        fields = ('first_name', 'last_name', 'phone_number',
                  'organization_membership', 'notes')

class UserDetailsVolunteerMixin(object):
    interests = models.TextField(verbose_name=_('Interests'))
    expertise = models.TextField(verbose_name=_('Expertise'))
    languages = models.CharField(max_length=50, verbose_name=_('Languages'))
    availability = models.CharField(max_length=50, verbose_name=_('Availability'))
    databases = models.TextField(verbose_name=_('Own Databases'))
    conflicts = models.TextField(
        verbose_name=_('Restrictions / Conflicts of Interest'))

    class Meta:
        fields = ('interests', 'expertise', 'languages', 'availability',
                  'databases', 'conflicts')

class UserDetailsRequesterMixin(object):
    industry = models.CharField(max_length=50, choices=INDUSTRY_TYPES,
                              verbose_name=_('Industry'))
    industry_other = models.CharField(max_length=50, verbose_name=_('Other Industry'))
    media = models.CharField(max_length=50, choices=MEDIA_TYPES,
                           verbose_name=_('Media Type'))
    circulation = models.CharField(max_length=50, choices=CIRCULATION_TYPES,
                                 verbose_name=_('Circulation (approximate '
                                                'per month)'))
    employer = models.CharField(max_length=50, verbose_name=_('Name of Employer'))
    title = models.CharField(max_length=50, verbose_name=_('Position / Job Title'))

    class Meta:
        fields = ('industry', 'industry_other', 'media', 'circulation',
                  'employer', 'title')


class ExpandoField(models.Model, DisplayMixin):
    label = models.CharField(max_length=100, blank=False, verbose_name=_('Label'))
    identifier = models.CharField(max_length=100, blank=False,
                                    verbose_name=_('Identifier'))
    kind = models.CharField(max_length=100, blank=False, verbose_name=_('Kind'))


class JSONResponseMixin(object):
    def get(self, request):
        return self.render_to_response(request)

    def post(self, request):
        return self.render_to_response(request)

    def render_to_response(self, request):
        "Returns a JSON response containing 'context' as payload"
        return self.get_json_response(self.convert_context_to_json())

    def get_json_response(self, content, **httpresponse_kwargs):
        "Construct an `HttpResponse` object."
        return HttpResponse(content,
                            content_type='application/json',
                            **httpresponse_kwargs)

    def convert_context_to_json(self):
        "Convert the context dictionary into a JSON object"
        # Note: This is *EXTREMELY* naive; in reality, you'll need
        # to do much more complex handling to ensure that arbitrary
        # objects -- such as Django model instances or querysets
        # -- can be serialized as JSON.
        def handledefault(o):
            if hasattr(o, "to_json"):
                return o.to_json()
            elif hasattr(o, "__dict__"):
                return o.__dict__
            else:
                raise ValueError("Not JSON serializable. Add to_json() or __dict__")
        return json.dumps(self.get_context_data(), default=handledefault)

