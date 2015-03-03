from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from id.mixins import *
from id.constdata import *

######## User profiles #################
class Profile(models.Model):
    user = models.OneToOneField(User)
    first_name = models.CharField(max_length=60, verbose_name=_("First Name"))
    last_name = models.CharField(max_length=60, verbose_name=_("Last Name"))
    abbr = models.CharField(max_length=8, verbose_name=_("Initials"))
    admin_notes = models.TextField(verbose_name=_("Admin Notes"))
    locale = models.CharField(max_length=10)

    requester_type = models.CharField(max_length=10, choices=REQUESTER_TYPES,
                                      verbose_name=_('Requester Type'))
    findings_visible = models.BooleanField(default=False,
                                      verbose_name=_('Findings Public'))
    is_for_profit = models.BooleanField(default=False,
                                   verbose_name=_('For-Profit?'))

    is_user = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_volunteer = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    old_google_id = models.CharField(max_length=100)

    phone_number = models.CharField(max_length=22)
    organization_membership = models.CharField(max_length=20)
    notes = models.TextField()
    address = models.CharField(max_length=50)
    city = models.CharField(max_length=50)
    province = models.CharField(max_length=50)
    postal_code = models.CharField(max_length=20)

    # Requester fields
    industry = models.CharField(max_length=20)
    industry_other = models.CharField(max_length=50)
    media = models.CharField(max_length=50)
    circulation = models.CharField(max_length=50)
    title = models.CharField(max_length=50)

    # Volunteer fields
    interests = models.TextField()
    expertise = models.TextField()
    languages = models.TextField()
    availability = models.TextField()
    databases = models.TextField()
    conflicts = models.TextField()


    def can_write_to(self, obj):
        '''
        return bool of whether this user can upload to somewhere
        XXX should be generalised further -- both other object types
        and other kinds of permissions
        '''
        if isinstance(obj, Ticket):
            return profile_in(self, [obj.requester, obj.responders, obj.volunteers])
        else: # XXX handling for entities here
            raise NotImplementedError("entity permissions not dealt with here")

    def tickets_for_user(self):
        return Ticket.query().filter(models.OR(
            Ticket.responders == self.key,
            Ticket.volunteers == self.key,
            Ticket.requester == self.key
        )).fetch()

    @property
    def groups_display(self):
        return ', '.join(x.capitalize() for x in ['user', 'staff', 'volunteer', 'admin'] if getattr(self, 'is_%s' % x))

    @property
    def num_requests(self):
        # XXX beware, this is expensive!
        if not tickets_per_user:
            set_ticket_counts()
        return tickets_per_user[self.key]

    @property
    def display_name(self):
        if self.first_name or self.last_name:
            return " ".join((self.first_name, self.last_name)).title()
        return self.full_name or self.name or self.email or ''

    @property
    def is_approved(self):
        return any((
            self.is_user, self.is_staff, self.is_volunteer, self.is_admin
            ))

    def get_account_request(self):
        '''Find the Account Request corresponding to this account
        '''
        ars = AccountRequest.query(AccountRequest.email == self.user.email())
        for ar in ars:
            if ar.approved == True: # try to get an approved one
                return ar

        #but fallback to something rather than nothing
        try:
            return ar
        except Exception:
            return None

    # Search Indexing -------------------

    def _post_put_hook(self, future):
        # Only index the user if they're in the staff group.
        if self.is_staff:
            index(self, only=self.Meta.search_fields,
                  index=self.Meta.index_name)
        else:
            unindex(self.key, self.Meta.index_name)

        # Maintain an alternate index for all users.
        if self.is_staff or self.is_admin or self.is_user:
            index(self, only=self.Meta.search_fields,
                  index=self.Meta.index_name_all)
        else:
            unindex(self.key, self.Meta.index_name_all)


    @classmethod
    def _post_delete_hook(cls, key, future):
        unindex(key, index=cls.Meta.index_name)
        unindex(key, index=cls.Meta.index_name_all)

    def to_select2(self):
        return {'id': self.key.urlsafe(), 'text': self.display_name}

    def __unicode__(self):
        return self.display_name

    @property
    def requester_type_verbose(self):
        if self.requester_type == 'subs':
            return _('Subsidized (OCCRP pays for everything)')
        elif self.requester_type == 'cost':
            return _('Covering cost (OCCRP pays for labor, requester pays costs'
                     ' of buying documents)')
        elif self.requester_type == 'cost_plus':
            return _('Covering cost+ (requester pays for documents, and also '
                     'for our work)')

    class Meta:
        pass
        #index_name = "userprofile_staff"
        #index_name_all = "userprofile_all"
        #search_fields = ['name', 'email', 'full_name']
        #fields = (('email', 'display_name', 'admin_notes',
        #          'requester_type', 'findings_visible', 'is_for_profit',
        #          'is_admin', 'is_staff', 'is_volunteer', 'is_user'
        #         ) +
        #         AddressMixin.Meta.fields +
        #         UserDetailsGenericMixin.Meta.fields +
        #         UserDetailsVolunteerMixin.Meta.fields +
        #         UserDetailsRequesterMixin.Meta.fields)
        # editable_fields = ('first_name', 'last_name') + tuple(x for x in fields if x not in ('display_name',))

######## External databases ############
class ExternalDatabase(models.Model, DisplayMixin):
    agency = models.CharField(max_length=500, blank=False, verbose_name=_('Agency / Name'))
    # agency_lower = models.ComputedProperty(lambda self: self.agency.lower())
    db_type = models.CharField(max_length=20, choices=DATABASE_TYPES,
                               verbose_name=_('Type of Database'))
    country = models.CharField(max_length=20, choices=DATABASE_COUNTRIES,
                               verbose_name=_('Country'))
    paid = models.BooleanField(default=False, verbose_name=_('Paid Database'))
    registration_required = models.BooleanField(default=False, verbose_name=_('Registration Required'))
    government_db = models.BooleanField(default=False, verbose_name=_('Government Database'))
    url = models.URLField(max_length=2000   , blank=False, verbose_name=_('URL'))
    notes = models.TextField(verbose_name=_('Notes'))
    blog_post = models.URLField(verbose_name=_('Blog Post'))
    video_url = models.URLField(verbose_name=_('YouTube Video Url'))

    def continent(self):
        return self._find_in_grouping(CONTINENTS)

    def region(self):
        return self._find_in_grouping(REGIONS)

    def _find_in_grouping(self, grouping):
        matches = [(k,v) for (k,v) in grouping.items() if self.country in v]
        if matches:
            return matches[0]
        else: # no continent found. This will happen for pseudo-countries
            return ('', set())

######## Entity relationships ##########
class Entity(models.Model, DisplayMixin, DriveMixin): # Expando
    comments = models.TextField(verbose_name=_('Comments'))
    relationships = models.ManyToManyField('Entity')

    @property
    def kind(self):
        return self.key.kind()

    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.__unicode__()

    def _pre_put_hook(self):
        self.update_drive_permissions()

    def _post_put_hook(self, future):
        self.Meta.search_fields.append('kind')
        index(self, only=self.Meta.search_fields, index='all')
        index(self, only=self.Meta.search_fields,
              index=self.key.kind().lower())

    @classmethod
    def _post_delete_hook(cls, key, future):
        unindex(key, index='all')
        unindex(key, index=key.kind())

    def _prop_list(self, fields):
        prop_list = []
        for f in fields:
            try:
                prop = getattr(type(self), f)
                verbose_name = prop._verbose_name
                value = self.get_display_value(f)
            except AttributeError:
                try:
                    query = ExpandoField.query().filter(
                        ExpandoField.kind == self.key.kind(),
                        ExpandoField.identifier == f).fetch()
                    if query:
                        prop = query[0]
                        verbose_name = prop.label
                        value = getattr(self, f)
                    else:
                        continue
                except Exception as e:
                    logging.warning("%r: %s" % (e, e.message))

            if value:
                prop_list.append((verbose_name, value))

        return prop_list

    @property
    def summary(self):
        return self._prop_list(self.Meta.summary_fields)

    @property
    def modal_details(self):
        ignored = self.Meta.modal_ignored_fields or []
        ignored.append("drive_folder_id")
        ignored.append("name")
        ignored.append("drive_shared_users")
        ignored.append("drive_shared_groups")
        fields = [f for f in self._properties.keys() if f not in ignored]
        return self._prop_list(fields)

    ## Shortcuts for relationships

    def relationships(self, cls_on_left=True, cls_on_right=True):
        '''get relationships
        default is all
        set cls_on_left = False to get only relationships where
         the other entity is on the right
        and vice versa
        '''
        ors = []
        if cls_on_left:
            ors.append(Relationship.left == self.key)
        if cls_on_right:
            ors.append(Relationship.right == self.key)
        return Relationship.query(ndb.OR(*ors))


    @property
    def addresses(self):
        return self.get_by_kind('Location')

    @property
    def people(self):
        return self.get_by_kind('Person')

    @property
    def companies(self):
        return self.get_by_kind('Company')

    @property
    def directors(self):
        '''only makes sense for companies'''
        pass

    def get_by_reltype(self, reltype):
        # inefficient, but it'll do for now
        # Note that this returns a list of relationships, not of the objects
        # to which the relationship applies
        # Also, we probably need a better way of handling directionality
        return [
            x for x in self.relationships().iter() if x.type == reltype]


    def get_by_kind(self, entity_kind):
        # inefficient, but it'll do for now
        # Note that this returns a list of relationships, not of the objects
        # to which the relationship applies
        # Also, we probably need a better way of handling directionality
        return [
            x for x in self.relationships(cls_on_left=False).iter() if x.left.get().kind == entity_kind] + [
            x for x in self.relationships(cls_on_right=False).iter() if x.right.get().kind == entity_kind]

    class Meta:
        pass
        #search_fields = None
        #summary_fields = None
        #modal_ignored_fields = None

class Relationship(models.Model, DisplayMixin, DriveMixin):  # Expando
    left = models.ForeignKey('Entity', blank=False, verbose_name=_('Entity One'), related_name="right_link")
    right = models.ForeignKey('Entity', blank=False, verbose_name=_('Entity Two'), related_name="left_link")
    type = models.CharField(max_length=70, blank=False, verbose_name=_('Type'),
                          choices=ALL_RELATIONSHIP_TYPES)
    left_name = models.CharField(max_length=50, verbose_name=_('Entity One'))
    right_name = models.CharField(max_length=50, verbose_name=_('Entity Two'))
    start = models.DateField(verbose_name=_('Start Date'))
    end = models.DateField(verbose_name=_('End Date'))
    comments = models.TextField(verbose_name=_('Comments'))

    def _pre_put_hook(self):
        super(Relationship, self)._pre_put_hook()
        self.left_name = unicode(self.left.get())
        self.right_name = unicode(self.right.get())

    # For future validation
    def get_types(self):
        if not self.left or not self.right:
            return None

        left_kind = self.left.kind()
        right_kind = self.right.kind()

        rpl = RELATIONSHIP_PRECEDENCE.index(left_kind)
        rpr = RELATIONSHIP_PRECEDENCE.index(right_kind)

        order = [(rpl, left_kind.upper()), (rpr, right_kind.upper())]
        order.sort()

        return getattr(globals(), "%s_%s_TYPES" % [k for i, k in order])

    def type_display(self):
        return get_choice_display(self.type, ALL_RELATIONSHIP_TYPES)


class Company(Entity):
    name = models.CharField(max_length=50, blank=False, verbose_name=_('Name'))
    name_variations = models.CharField(max_length=50, verbose_name=_('Name Variations'))  # Repeated
    jurisdiction = models.CharField(max_length=70, choices=COUNTRIES,
                                  verbose_name=_('Jurisdiction Registered'))
    type = models.CharField(max_length=70, choices=COMPANY_TYPES,
                          verbose_name=_('Form of Company'))
    status = models.CharField(max_length=70, choices=COMPANY_STATUS,
                            verbose_name=_('Status'))
    registered = models.DateField(verbose_name=_('Date Registered'))
    dissolved = models.DateField(verbose_name=_('Date Dissolved'))


class Person(Entity):
    first_name = models.CharField(max_length=50, blank=False,
                                    verbose_name=_('First Name'))
    middle_name = models.CharField(max_length=50, verbose_name=_('Middle Name'))
    last_name = models.CharField(max_length=50, verbose_name=_('Last Name'))
    name_variations = models.CharField(max_length=50, verbose_name=_('Name Variations'))  # Repeated
    birth = models.DateField(verbose_name=_('Date of Birth'))
    death = models.DateField(verbose_name=_('Date of Death'))
    sex = models.CharField(max_length=70, choices=SEX, verbose_name=_('Sex'))
    nationalities = models.CharField(max_length=50, verbose_name=_('Nationalities'))  # Repeated
    id_numbers = models.CharField(max_length=50, verbose_name=_('ID Numbers'))  # Repeated

    def __unicode__(self):
        name = filter(None, [self.first_name, self.middle_name,
                             self.last_name])
        return ' '.join(name)


class Location(Entity, AddressMixin):
    name = models.CharField(max_length=50, blank=False, verbose_name=_('Name'))

    def __unicode__(self):
        name = filter(None, [self.name, self.address, self.city,
                             self.province, self.postal_code, self.country])
        return ', '.join(name)


######## Data requests #################
class Ticket(models.Model, DriveMixin, ModelDiffMixin, DisplayMixin):  # polymodel.PolyModel
    """
    Common fields for all ticket types

    Note: Implement volunteers as a separate list of fields from responders,
    so that permissions stay simple.
    """
    # Staff-facing fields
    requester = models.ForeignKey(User, related_name="ticket_requests")
    requester_type = models.CharField(max_length=70, choices=REQUESTER_TYPES,
                                    verbose_name=_('Requester Type'))
    responders = models.ManyToManyField(User, related_name="tickets_responded")

    volunteers = models.ManyToManyField(User, related_name="tickets_volunteered")

    created = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=70, choices=TICKET_STATUS, default='new')
    status_updated = models.DateTimeField(auto_now=True)
    findings_visible = models.BooleanField(default=False,
                                           verbose_name=_('Findings Public'))
    is_for_profit = models.BooleanField(default=False,
                                        verbose_name=_('For-Profit?'))
    is_public = models.BooleanField(default=False,
                                    verbose_name=_('Public?'))
    flagged = models.BooleanField(default=False)
    user_pays = models.BooleanField(default=True)
    entities = models.ManyToManyField(Entity)

    def most_fields(self):
        '''Return an iterator of tuples (verbose name, display value)
        for all fields which can be shown to everybody on the ticket'''
        output = [
            (_('Summary'), self.summary),
            (_('Requested by'), self.requester.get().display_name),
        ]
        return output

    # User-facing fields
    @property
    def summary(self):
        return ""

    deadline = models.DateField(blank=False, verbose_name=_('Deadline'))
    sensitive = models.BooleanField(verbose_name=_('Sensitive?'), default=False)

    def _pre_put_hook(self, future=None):
        # Copy default requester settings into the ticket if it's not been
        # saved yet.
        if not self.key.id() and self.requester:
            requester = self.requester.get()
            self.requester_type = requester.requester_type
            self.findings_visible = requester.findings_visible
            self.is_for_profit = requester.is_for_profit

        if self.responder:
            # slowly migrate the datas.
            if self.responder not in self.responders:
                self.responders.append(self.responder)
            self.responder = None
        self.update_drive_permissions()

    def actors(self):
        """
        Get a list of actors for a given ticket, being the requester and
        responder
        """
        return [actor for actor in
                [self.requester, ] + self.responders + self.volunteers
                if actor]

    def join_user(self, actor):
        """
        Adds an existing UserProfile object to the list of ticket
        contributors, if the user if a volunteer, they're forced into the
        volunteers category.

        Args:
            actor (UserProfile Key) - an actor to add to the ticket.

        Returns:
            boolean - whether the user was added or not.
        """

        if isinstance(actor, ndb.Key):
            actor = actor.get()

        if actor.key not in self.actors():
            if actor.is_volunteer:
                self.volunteers.append(actor.key)
            else:
                self.responders.append(actor.key)
            self.put()
            return True

        return False

    def leave_user(self, actor):
        """
        Remove all mentions of a UserProfile from the list of responders and
        volunteers on a ticket.

        Args:
            actor (UserProfile Key) - an actor who wants to leave the ticket.
        """

        if not isinstance(actor, ndb.Key):
            actor = actor.key

        self.responders = [a for a in self.responders if a != actor]
        self.volunteers = [a for a in self.volunteers if a != actor]
        self.put()

    def permalink(self, include_domain=False):
        return "%s%s" % (
            ROOT_URL if include_domain else "",
            webapp2.uri_for('request_details', ticket_id=self.key.id()))

    def set_derivative_properties(self):
        diff = self.diff
        # if status has been explicitly set, don't second-guess it
        if 'status' in diff['changed_properties']:
            self.status_updated = datetime.datetime.now()
            return

        if getattr(diff['old'], 'status', None) == u'new':
            #new tickets become in progress when somebody is assigned
            logging.info('new ticket')
            if self.responders_len > 0:
                self.status = 'in-progress'

    def put(self, **kwargs):
        """
        Optional kwargs that are popped are:
        generate_update - whether or not to detect changes to important
          fields and generate a TicketUpdate
        comment - if generate_update is True, this should be a comment for the
          TicketUpdate
        """
        # Override put() so we can toggle whether an update gets generated
        generate_update = kwargs.pop('generate_update', True)
        comment = kwargs.pop('comment', '')

        if generate_update:
            # Get changed properties before saving
            self.set_derivative_properties()
            diff = self.diff

            super(Ticket, self).put(**kwargs)

            # Pass changed properties so proper update can be generated
            self.generate_update(comment, **diff)
        else:
            super(Ticket, self).put(**kwargs)

    def generate_update(self, comment, old=None, changed_properties=None):
        """
        Create a TicketUpdate instance based on the ticket changes
        """
        kwargs = {
            'parent': self.key,
            'ticket': self.key,
            'author': get_current_user_profile().key,
            'comment': comment,
        }

        # Map status changes to ticket update types
        if self.status == u'new':
            kwargs['update_type'] = 'open'
        elif 'status' in changed_properties:
            if self.status == 'cancelled':
                kwargs['update_type'] = 'cancel'
            elif self.status == 'closed':
                kwargs['update_type'] = 'close'
            elif self.status == 'in-progress':
                kwargs['update_type'] = 'update'
        elif 'flagged' in changed_properties and self.flagged:
            kwargs['update_type'] = 'flag'
        elif ('entities' in changed_properties
              and len(self.entities) > len(old.entities)):
            kwargs['update_type'] = 'entities_attached'

        if 'update_type' not in kwargs:
            logging.warn('ticket update type not specified')
            kwargs['update_type'] = 'update'

        if 'update_type' in kwargs:
            TicketUpdate(**kwargs).put()

    def permalink(self):
        return webapp2.uri_for('request_details', ticket_id=self.key.id(),
                               _full=True)

    def ticket_type_display(self):
        return get_choice_display(self.ticket_type, TICKET_TYPES)

    def status_display(self):
        return get_choice_display(self.status, TICKET_STATUS)

    def requester_type_display(self):
        return get_choice_display(self.requester_type, REQUESTER_TYPES)

    def is_open(self):
        return self.status in OPEN_TICKET_STATUSES

    def mark_charges_paid(self, paid_status):
        """
        Mark the ticket as paid, and all the charges associated with it.
        """
        charges = TicketCharge.query(
            TicketCharge.reconciled == False, ancestor=self.key).fetch()

        for charge in charges:
            charge.reconciled = True
            charge.paid_status = paid_status

        ndb.put_multi(charges)

    def fetch_responders(self):
        # XXX deprecated? I can't find anything calling this
        # TODO: Extend list comp here for muliple responders
        logging.info("deprecated fetch_responders called")
        logging.info(traceback.format_stack())
        return ndb.get_multi([self.responder]) if self.responder else []


class PersonTicket(Ticket):
    """ Person ownership request """
    ticket_type = 'person_ownership'
    name = models.CharField(max_length=50, blank=False, verbose_name=_('Name'))
    aliases = models.CharField(max_length=100, blank=True, verbose_name=_('Aliases'))
    background = models.TextField(blank=False, verbose_name=_('Background'))
    biography = models.TextField(blank=False, verbose_name=_('Biography'))
    family = models.TextField(blank=True, verbose_name=_('Family'))
    business_activities = models.TextField(
        blank=False,
        verbose_name=_('Business Activities'))
    dob = models.DateField(blank=False, verbose_name=_('Date of Birth'))
    birthplace = models.CharField(max_length=50,
        blank=False,
        verbose_name=_('Place of Birth'))
    initial_information = models.TextField(
        blank=False,
        verbose_name=_('Where have you looked?'))
    location = models.CharField(max_length=50,
        blank=False,
        verbose_name=_('Location'))

    @property
    def summary(self):
        return "Person: %s" % smart_truncate(self.name, 150)


    def most_fields(self):
        '''Return an iterator of tuples (verbose name, display value)
        for all fields which can be shown to everybody on the ticket'''
        output = Ticket.most_fields(self)
        for i in ('name', 'aliases', 'background', 'biography', 'family',
                  'business_activities', 'dob', 'birthplace',
                  'initial_information', 'location'):
            output.append((self._properties[i]._verbose_name, self.get_display_value(i)))
        return output


class CompanyTicket(Ticket):
    """ Company ownership request """
    ticket_type = 'company_ownership'
    name = models.CharField(max_length=50,
        blank=False,
        verbose_name=_('Company Name'))
    country = models.CharField(max_length=70, choices=COUNTRIES,
                             blank=False,
                             verbose_name=_('Country Registered'))
    background = models.TextField(blank=False, verbose_name=_('Background'))
    sources = models.TextField(blank=False, verbose_name=_('Sources'))
    story = models.TextField(blank=False, verbose_name=_('Your Story'))
    connections = models.CharField(max_length=50, verbose_name=_('Connected People')) # Repeated

    @property
    def summary(self):
        return "Company: %s" % smart_truncate(self.name, 150)

    def most_fields(self):
        '''Return an iterator of tuples (verbose name, display value)
        for all fields which can be shown to everybody on the ticket'''
        output = Ticket.most_fields(self)
        for i in ('name', 'country', 'background', 'sources', 'story',
                  'connections'):
            output.append((self._properties[i]._verbose_name, self.get_display_value(i)))
        return output

class OtherTicket(Ticket):
    """ Any other request """
    ticket_type = 'other'
    question = models.TextField(blank=False,
                                verbose_name=_('What do you want to know?'))

    @property
    def summary(self):
        words = unicode(self.question).split(" ")
        text = ""
        for word in words:
            text += word + " "
            if len(text) > 120: break
        return "Question: %s" % text.strip()

class TicketUpdate(models.Model):
    update_type = models.CharField(max_length=70, choices=TICKET_UPDATE_TYPES,
                                 default=TICKET_UPDATE_TYPES[0][0])
    author = models.ForeignKey(User, blank=False)  # requester or responder
    ticket = models.ForeignKey(Ticket, blank=False)
    created = models.DateTimeField(auto_now_add=True)
    comment = models.TextField()

    # if you plan to use the extra_relation key for any ticket updates
    # make sure the model that you're relating to implements a method with
    # signature: def to_ticket_update(self, update): which returns a formatted
    # and translated string to be output along with any ticket update comment
    # text.
    # extra_relation = models.ForeignKey()

    def _post_put_hook(self, future):
        """
        After the TicketUpdate has been `put`, notify everyone of the update
        """
        # XXX: Temporarily disabled because of bugginess for Oct. 12/13 demo.
        self.notify()

    def get_notified(self, ticket):
        """
        Get a list of people who need to be notified of this TicketUpdate
        """
        recipient_types = config['ticket_notifications'][self.update_type]
        recipients = []
        for r in recipient_types:
            if r == 'requester':
                recipients.append(ticket.requester.get())
            elif r == 'responders':
                recipients = recipients + ticket.fetch_responders()
            elif r == 'admin':
                admin = UserProfile.query(UserProfile.is_admin == True).fetch()
                recipients = recipients + admin
        return recipients

    def notify(self):
        """
        Notify all required parties of an update

        Uses the ticket key ID to populate the notification email address
        template.
        """
        ticket = self.ticket.get()

        actors = self.get_notified(ticket)
        # ensure any actor triggering a ticket update belongs to the ticket.
        if not self.author in actors:
            self.ticket.get().join_user(self.author)

        for user in actors:
            with templocale(user.locale or 'en'):
                subject = unicode(_("[Request %s] - %s") % (
                    self.update_type_display(), ticket.summary))
                email_notification(
                    sender_suffix=ticket.key.id(),
                    to=user.email,
                    subject=subject,
                    template='mail/ticket_update.html',
                    context={
                        'update': self,
                        'url': ticket.permalink()
                    })

    def update_type_display(self):
        return get_choice_display(self.update_type, TICKET_UPDATE_TYPES)

class DecimalProperty(models.IntegerField):
    def _validate(self, value):
        if not isinstance(value, Decimal):
            raise TypeError('decimal expected, %s found' % type(value))

    def _to_base_type(self, value):
        # decimal -> int
        return int(value * 100)

    def _from_base_type(self, value):
        # int -> decimal
        return Decimal(value) / 100

class TicketCharge(models.Model, DisplayMixin):
    """
    An individual charge to a ticket.

    the parent entity should always be the ticket that it belongs to.
    """

    ticket = models.ForeignKey(Ticket, blank=False)
    user = models.ForeignKey(User, blank=False)

    # comment on what the charge is for
    item = models.CharField(max_length=50, blank=False)

    # cost in USD
    cost = DecimalProperty()

    # cost in original currency
    cost_original_currency = DecimalProperty()
    original_currency = models.CharField(max_length=50, )

    # whether the bill has been reconciled or not
    reconciled = models.BooleanField(default=False)
    reconciled_date = models.DateTimeField()
    paid_status = models.CharField(max_length=70, choices=PAID_STATUS)

    # when the charge was created
    created = models.DateTimeField(auto_now_add=True)

    def to_ticket_update(self, update):
        text = _(
            "Item: %(item)s\nCost (USD): $%(cost)s\n"
            ) % { 'item': self.item,
                  'cost': self.cost,}
        if self.cost_original_currency:
            text += "Cost (original currency): %(cost_original_currency)s %(original_currency)s" % {
            'cost_original_currency': self.cost_original_currency or '',
            'original_currency': self.original_currency or ''}
        return text

    def _pre_put_hook(self):
        # fill in the reconciled date if it's missing.
        if self.reconciled and not self.reconciled_date:
            self.reconciled_date = datetime.datetime.now()

    @classmethod
    def outstanding_charges(cls, charges, pluck=None):
        """
        Gathers all the cost items for supplied charges that are un-reconciled.

        @param charges: A list of TicketCharges
        @param pluck: (None | Property) if pluck is supplied, it will pluck
                      the supplied property name from the charge.
        """
        outstanding = []
        for charge in charges:
            if not charge.reconciled:
                if pluck:
                    outstanding.append(getattr(charge, pluck._name))
                else:
                    outstanding.append(charge)
        return outstanding

    @classmethod
    def customer_charges(cls, user_key, reconciled=None, pluck=None):
        """
        Get all charges for a user in the system, doesn't care about tickets.

        @param user_key: The user you want to filter on
        @param reconciled: Whether you want reconciled or un-reconciled charges
        @param pluck: (None | Property) if pluck is supplies, it will pluck
                      the supplied property name from the charge.
        """

        query = cls.query(cls.user == user_key)

        if reconciled is not None:
            query = query.filter(cls.reconciled == reconciled)

        charges = query.fetch()

        if pluck:
            return [getattr(charge, pluck._name) for charge in charges]
        else:
            return charges

######## Account management ############
class AccountRequest(models.Model, DisplayMixin, AddressMixin, UserDetailsGenericMixin): # polymodel
    request_type = 'generic'
    user_profile = models.ForeignKey(User, blank=False)
    approved = models.BooleanField(default=False, verbose_name=_('Approved'))
    email = models.CharField(max_length=50, blank=False, verbose_name=_('Email Address'))
    date_created = models.DateTimeField(auto_now_add=True,
                                        verbose_name=_('Date Created'))

    # temporary fix for updated profiles
    already_updated = models.BooleanField(default=False)

    admin_only_fields = ('approved', 'email', 'date_created')
    # Most fields for details are pulled in from UserDetailsGenericMixin,
    # so that they can be shared with UserProfile

    GROUPS = []
    MAIL_TEMPLATE = 'accountrequest/mail_notification.html'

    class Meta:
        pass
        #fields = UserDetailsGenericMixin.Meta.fields + AddressMixin.Meta.fields + ('approved', 'email',) #XXX see if we need this
        #user_visible_fields = tuple(x for x in fields if x not in AccountRequest.admin_only_fields)

    @classmethod
    def pending_for(cls, user):
        return cls.query().filter(
            cls.email == user.email()).fetch()

    @property
    def full_name(self):
        return "%s %s" % (self.first_name, self.last_name)

    def get_display_value(self, property_name):
        if property_name != 'approved':
            return super(AccountRequest, self).get_display_value(property_name)
        else:
            return ('--' if self.approved is None
                    else _('Yes') if self.approved is True
                    else _('No'))

    def fields_for_userprofile(self):
        return self.Meta.fields # XXX duplication -- move to just Meta.fields
        return ['request_type', 'first_name', 'last_name', 'phone_number',
                'organization_membership', 'notes']

    def enhance_userprofile(self):
        user = self.user_profile.get()
        fields = self.fields_for_userprofile()
        for i in fields:
            setattr(user, i, getattr(self, i))
            logging.info('setting %s to %s based on %s' % (i, getattr(user, i), getattr(self, i)))
        #try doing one manually
        # for some reason, we cannot use setattr
        user.request_type = self.request_type
        # user.first_name = self.first_name
        # user.last_name = self.last_name
        user.phone_number = self.phone_number
        user.organization_membership = self.organization_membership
        user.notes = self.notes
        user.address = self.address
        user.city = self.city
        user.province = self.province
        user.postal_code = self.postal_code

        if self.request_type == 'requester':
            user.industry = self.industry
            user.industry_other = self.industry_other
            user.media = self.media
            user.circulation = self.circulation
            user.title = self.title
        if self.request_type == 'volunteer':
            user.interests = self.interests
            user.expertise = self.expertise
            user.languages = self.languages
            user.availability = self.availability
            user.databases = self.databases
            user.conflicts = self.conflicts
        user.put()
        self.already_updated = True
        self.put()

    def approve(self, groups_to_add=['user']):
        """
        Adds the Account Request's email address to the appropriate Google
        groups, and marks the request as approved.
        """
        # groups sync is deprecated
        #groups_service = groups.Groups.system_instance()
        #for group in self.GROUPS:
        #    groups_service.add_to(config[group], self.email)

        # XXX this is a hack, on the way to eliminating google-based permisssions
        # entirely
        # but it'll take a while to get there
        for g in groups_to_add:
            g_name = 'is_%s' % g
            setattr(self.user_profile.get(), g_name, True)

        self.enhance_userprofile()
        self.approved = True
        self.put()
        self.notify_approved()

    def reject(self):
        """
        Removes the user from the group!
        """
        # groups is deprecated
        #groups_service = groups.Groups.system_instance()
        #for group in self.GROUPS:
        #    groups_service.remove_from(config[group], self.email)

        self.approved = False
        self.put()
        self.notify_rejected()

    def notify_received(self):
        email_notification(
            to=self.email,
            subject=unicode(_('Your Account Request was received')),
            template='mail/account_request/received.html',
            context={'request': self}
        )
        for admin in UserProfile.query(UserProfile.is_admin == True).fetch():
            with templocale(admin.locale or 'en'):
                email_notification(
                    to=admin.email,
                    subject=unicode(_('An Account Request was received')),
                    template='mail/account_request/received_admin.html',
                    context={'request': self}
                    )

    def notify_approved(self):
        email_notification(
            to=self.email,
            subject=unicode(_('An update to your Account Request')),
            template='mail/account_request/approved.html',
            context={'request': self}
        )

    def notify_rejected(self):
        email_notification(
            to=self.email,
            subject=unicode(_('Your Account Request was rejected')),
            template='mail/account_request/rejected.html',
            context={'request': self}
        )

    def url(self, action='edit'):
        return '/admin/accountrequest/%s/%s/' % (self.key.urlsafe(), action)

class RequesterRequest(AccountRequest, UserDetailsRequesterMixin):
    request_type = 'requester'

    GROUPS = ['groups_all_id', 'groups_users_id']

    def fields_for_userprofile(self):
        return self.Meta.fields

    class Meta:
        pass
        # fields = AccountRequest.Meta.fields + UserDetailsRequesterMixin.Meta.fields
        # user_visible_fields = tuple(x for x in fields if x not in AccountRequest.admin_only_fields)

class VolunteerRequest(AccountRequest, UserDetailsVolunteerMixin):
    request_type = 'volunteer'

    GROUPS = ['groups_all_id', 'groups_volunteer_id']

    def fields_for_userprofile(self):
        return self.Meta.fields

    class Meta:
        pass
        # fields = AccountRequest.Meta.fields + UserDetailsVolunteerMixin.Meta.fields
        # user_visible_fields = tuple(x for x in fields if x not in AccountRequest.admin_only_fields)


class DatabaseScrapeRequest(models.Model):
    url = models.URLField(blank=False, verbose_name=_("URL"))
    name = models.CharField(max_length=200, verbose_name=_("Name"))
    description = models.TextField(verbose_name=_("Description"))
    # plusones = models.ManyToManyField(User)

    # def plusone(self, user):
    #    self.plusone.add(user)

    #def minusone(self, user):
    #    self.plusone.remove(user)

