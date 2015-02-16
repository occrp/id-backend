import json
from django.db import models
from django.http import HttpResponse
from django.utils.translation import ugettext_lazy as _

from id.constdata import *

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


class DriveMixin(object):
    """ Fields necessary for supporting Drive uploads. """
    drive_folder_id = models.CharField(max_length=200)
    drive_shared_users = models.TextField()
    drive_shared_groups = models.TextField()
    _use_cache = False

    def permissions_changed(self):
        if 'groups_admin_id' not in self.drive_shared_groups:
            self.drive_shared_groups.append('groups_admin_id')
        old = self.key.get()
        new = self
        if (old.drive_shared_users != new.drive_shared_users or
                old.drive_shared_groups != new.drive_shared_groups):
            return True
        return False

    def update_drive_permissions(self):
        if not self.drive_folder_id:
            # Deliberately omitting 'groups_admin_id' so that
            # next save will trigger permissions_changed.
            self.drive_shared_groups = ['groups_staff_id']
            return  # Cannot have had files uploaded yet
        elif not self.permissions_changed():
            return

        # Clear all old permissions
        drive = Drive.system_instance()
        drive.clear_permissions(self.drive_folder_id)

        # If ticket, make requestor and responder readers
        share_with = []
        if getattr(self, 'requester', None):
            share_with.append(self.requester.get().email)
        if getattr(self, 'responders', None):
            for responder in self.responders:
                share_with.append(responder.get().email)

        # Make all named users readers
        if self.drive_shared_users:
            share_with = share_with + self.drive_shared_users

        if share_with:
            drive.share([self.drive_folder_id], share_with, 'user', 'reader')

        # Make all groups readers
        if self.drive_shared_groups:
            group_emails = [config[g] for g in self.drive_shared_groups]
            drive.share(
                [self.drive_folder_id], group_emails, 'group', 'reader')

        # Make public if necessary
        if 'groups_all_id' in self.drive_shared_groups:
            drive.share(
                [self.drive_folder_id], [''], 'anyone', 'reader')

    def _create_drive_folder(self):
        if not self.drive_folder_id:
            drive = Drive.system_instance()
            folder_human_label = key_to_json(self.key)
            self.drive_folder_id = drive.ensure_folder(folder_human_label)
            self.put()
        return self.drive_folder_id

    def _add_file(self, fh, title):
        drive = Drive.system_instance()
        mimetype = 'application/pdf' # XXX fixme
        drive._upload_file(fh = fh,
                           folder_id = self._create_drive_folder(),
                           title = title,
                           mimetype=mimetype)

    def list_files(self):
        pass


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

