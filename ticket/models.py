from itertools import chain

#from django.contrib.auth.models import User
from settings.settings import AUTH_USER_MODEL # as per https://docs.djangoproject.com/en/dev/topics/auth/customizing/#referencing-the-user-model
from django.db import models
from django.utils.translation import ugettext_lazy as _

from core.mixins import ModelDiffMixin, DisplayMixin

from constants import *
from utils import *
import datetime

######## Data requests #################
class Ticket(models.Model, ModelDiffMixin, DisplayMixin):  # polymodel.PolyModel
    """
    Common fields for all ticket types

    Note: Implement volunteers as a separate list of fields from responders,
    so that permissions stay simple.
    """
    ticket_type = ""
    # Staff-facing fields
    requester = models.ForeignKey(AUTH_USER_MODEL, related_name="ticket_requests")
    requester_type = models.CharField(blank=False, max_length=70, choices=REQUESTER_TYPES,
                                    verbose_name=_('Requester Type'), default='subs')
    responders = models.ManyToManyField(AUTH_USER_MODEL, related_name="tickets_responded")

    volunteers = models.ManyToManyField(AUTH_USER_MODEL, related_name="tickets_volunteered")

    created = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=70, choices=TICKET_STATUS, default='new')
    status_updated = models.DateTimeField(default=datetime.datetime.now, null=False)
    findings_visible = models.BooleanField(default=False,
                                           verbose_name=_('Findings Public'))
    is_for_profit = models.BooleanField(default=False,
                                        verbose_name=_('For-Profit?'))
    is_public = models.BooleanField(default=False,
                                    verbose_name=_('Public?'))
    user_pays = models.BooleanField(default=True)
    deadline = models.DateField(null=True, blank=True, verbose_name=_('Deadline'))
    sensitive = models.BooleanField(default=False, verbose_name=_('Sensitive?'))

    tag_id = models.CharField(max_length=60, blank=True)    # Refers to this Ticket's Podaci tag.

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

    def get_type_icon(self):
        if self.ticket_type == 'person_ownership': return 'user'
        elif self.ticket_type == 'company_ownership': return 'building'
        else: return 'question'

    def get_status(self):
        return dict(TICKET_STATUS).get(self.status, _('Unknown'))

    def get_status_icon(self):
        return dict(TICKET_STATUS_ICONS).get(self.status, 'question')

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

    def actors(self, include_self=True):
        """
        Get a list of actors for a given ticket, being the requester and
        responder
        """
        actors = [actor for actor in
                  list(chain(self.responders.all(), self.volunteers.all())) if actor]
        if include_self:
            actors.append(self.requester)
        return actors

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
    name = models.CharField(max_length=512, blank=False, verbose_name=_('Name'))
    aliases = models.TextField(blank=True, verbose_name=_('Aliases'), help_text=_("Other names they are known by"))
    background = models.TextField(blank=False, verbose_name=_('Background'))
    biography = models.TextField(blank=False, verbose_name=_('Biography'))
    family = models.TextField(blank=True, verbose_name=_('Family'))
    business_activities = models.TextField(
        blank=False,
        verbose_name=_('Business Activities'))
    dob = models.DateField(null=True, blank=True, verbose_name=_('Date of Birth'))
    birthplace = models.CharField(max_length=128,
        blank=False,
        verbose_name=_('Place of Birth'))
    initial_information = models.TextField(
        blank=False,
        verbose_name=_('Where have you looked?'))
    location = models.CharField(max_length=128,
        blank=False,
        verbose_name=_('Location'))

    @property
    def summary(self):
        return "%s" % smart_truncate(self.name, 150)


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
    name = models.CharField(max_length=512,
        blank=False,
        verbose_name=_('Company Name'))
    country = models.CharField(max_length=100, choices=COUNTRIES,
                             blank=False,
                             verbose_name=_('Country Registered'))
    background = models.TextField(blank=False, verbose_name=_('Background'))
    sources = models.TextField(blank=False, verbose_name=_('Sources'))
    story = models.TextField(blank=False, verbose_name=_('Your Story'))
    connections = models.TextField(blank=True, verbose_name=_('Connected People'))

    @property
    def summary(self):
        return "%s" % (smart_truncate(self.name, 150))

    def get_country(self):
        return dict(COUNTRIES).get(self.country, self.country)

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
        return "%s" % text.strip()

class TicketUpdate(models.Model):
    update_type = models.CharField(max_length=70, choices=TICKET_UPDATE_TYPES,
                                   default=TICKET_UPDATE_TYPES[0][0])
    author = models.ForeignKey(AUTH_USER_MODEL, blank=False)  # either requester, or responder
    ticket = models.ForeignKey(Ticket, blank=False)
    created = models.DateTimeField(auto_now_add=True)
    comment = models.TextField()
    is_removed = models.BooleanField(default=False)

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
                admin = UserProfile.query(UserProfile.is_superuser == True).fetch()
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
                    template='mail/ticket_update.jinja',
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

class Budget(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField(blank=True)

    def get_payment_total(self):
        total = 0
        for charge in TicketCharge.objects.filter(budget=self):
            total += charge.cost
        return total

    def __unicode__(self):
        return self.name

class TicketCharge(models.Model, DisplayMixin):
    """
    An individual charge to a ticket.

    the parent entity should always be the ticket that it belongs to.
    """

    ticket = models.ForeignKey(Ticket, blank=False)
    user = models.ForeignKey(AUTH_USER_MODEL, blank=False)

    # comment on what the charge is for
    item = models.CharField(max_length=64, blank=False)
    budget = models.ForeignKey(Budget, blank=True, null=True)

    # cost in USD
    cost = DecimalProperty()

    # cost in original currency
    cost_original_currency = DecimalProperty()
    original_currency = models.CharField(max_length=50, )

    # whether the bill has been reconciled or not
    reconciled = models.BooleanField(default=False)
    reconciled_date = models.DateTimeField(blank=True, null=True)
    paid_status = models.CharField(max_length=70, choices=PAID_STATUS, blank=False)

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