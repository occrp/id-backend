from itertools import chain

#from django.contrib.auth.models import User
from settings.settings import AUTH_USER_MODEL # as per https://docs.djangoproject.com/en/dev/topics/auth/customizing/#referencing-the-user-model
from django.db import models
from django.utils.translation import ugettext_lazy as _

from core.mixins import DisplayMixin, NotificationMixin
from core.countries import COUNTRIES
from podaci.models import PodaciFile

from constants import *
from utils import *
import datetime


######## Data requests #################

class Ticket(models.Model, DisplayMixin, NotificationMixin):
    """
    Common fields for all ticket types
    """
    ticket_type = ""
    # Staff-facing fields
    requester = models.ForeignKey(AUTH_USER_MODEL, related_name="ticket_requests", db_index=True)
    requester_type = models.CharField(blank=False, max_length=70, choices=REQUESTER_TYPES,
                                    verbose_name=_('Requester Type'), default='subs')
    responders = models.ManyToManyField(AUTH_USER_MODEL, related_name="tickets_responded")

    created = models.DateTimeField(default=datetime.datetime.now, null=False)
    status = models.CharField(max_length=70, choices=TICKET_STATUS, default='new', db_index=True)
    status_updated = models.DateTimeField(default=datetime.datetime.now, null=False)
    findings_visible = models.BooleanField(default=False,
                                           verbose_name=_('Findings Public'))
    is_for_profit = models.BooleanField(default=False,
                                        verbose_name=_('For-Profit?'))
    is_public = models.BooleanField(default=False,
                                    verbose_name=_('Public?'), help_text=_('Are you okay with the findings becoming public immediately?'))
    user_pays = models.BooleanField(default=True)
    deadline = models.DateField(null=True, blank=True, verbose_name=_('Deadline'), help_text=_('How soon do you need this request fulfilled? We will try to meet your deadline, but please note that our researchers are quite busy -- give them as much time as you possibly can!'))
    sensitive = models.BooleanField(default=False, verbose_name=_('Sensitive?'))
    whysensitive = models.CharField(max_length=150, blank=True, verbose_name=_('Why is it sensitive?'))

    files = models.ManyToManyField(PodaciFile, related_name="tickets")

    def get_actual_ticket(self):
        try:
            return self.personticket
        except:
            pass
        try:
            return self.companyticket
        except:
            pass
        try:
            return self.otherticket
        except:
            pass

    def get_csv_header(self):
        return ["ticket_type", "summary", "requester_type",
                "status"]

    def as_sequence(self):
        # FIXME
        return [] # getattr(self, i) for i in self.get_csv_header()]

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
        if hasattr(self, "personticket"):
            return PersonTicket.get_summary(self.personticket)
        elif hasattr(self, "companyticket"):
            return CompanyTicket.get_summary(self.companyticket)
        else:
            return OtherTicket.get_summary(self.otherticket)

    def get_country(self):
        return None

    def get_type_icon(self):
        if self.ticket_type == 'person_ownership': return 'user'
        elif self.ticket_type == 'company_ownership': return 'building'
        else: return 'question'

    def get_status(self):
        return dict(TICKET_STATUS).get(self.status, _('Unknown'))

    def get_status_icon(self):
        return dict(TICKET_STATUS_ICONS).get(self.status, 'question')

    def is_responder(self, user):
        return self.responders.filter(id=user.id).count()

    def actors(self):
        """
        Get a list of actors for a given ticket, being the requester and
        responder
        """
        return self.responders.all()

    def join_user(self, actor):
        """
        Adds an existing User to the list of ticket
        contributors.

        Args:
            actor (UserProfile Key) - an actor to add to the ticket.

        Returns:
            boolean - whether the user was added or not.
        """

        if actor in self.actors():
            return False

        self.responders.add(actor)
        self.notify(u"%s has joined ticket %s (%d) as a %s" % (actor, self.summary, self.id, ["responder", "volunteer"][actor.is_volunteer]), actor, 'ticket_details', {'ticket_id': self.pk}, 'join')
        return True

    def leave_user(self, actor):
        """
        Remove all mentions of a UserProfile from the list of responders on a ticket.

        Args:
            actor (UserProfile Key) - an actor who wants to leave the ticket.
        """
        self.responders.remove(actor)
        self.notify(u"%s has left ticket %s (%d)" % (actor, self.summary, self.id), actor, 'ticket_details', {'ticket_id': self.pk}, 'leave')

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

    def ticket_type_display(self):
        return get_choice_display(self.ticket_type, TICKET_TYPES)

    def status_display(self):
        return get_choice_display(self.status, TICKET_STATUS)

    def requester_type_display(self):
        return get_choice_display(self.requester_type, REQUESTER_TYPES)

    def is_open(self):
        return self.status in OPEN_TICKET_STATUSES

    def resolution_time(self):
        if self.status != 'closed':
            return datetime.timedelta(0)

        starttime = None
        endtime = None
        for update in self.ticketupdate_set.all():
            if update.update_type == "open":
                starttime = update.created
            elif update.update_type == "close":
                endtime = update.created

        if starttime and endtime:
            return endtime - starttime

        return datetime.timedelta(0)

    def to_json(self):
        return {
            'id': self.id,
            'ticket_type': self.ticket_type,
            'requester': self.requester,
            'requester_type': self.requester_type,
            'created': self.created,
            'status': self.status,
            'summary': self.summary,
            'is_for_profit': self.is_for_profit,
            'is_public': self.is_public,
            'is_open': self.is_open(),
            'deadline': self.deadline,
            'sensitive': self.sensitive
        }

class PersonTicket(Ticket):
    """ Person ownership request """
    ticket_type = 'person_ownership'
    name = models.CharField(max_length=512, blank=False, verbose_name=_('First/other names'))
    surname = models.CharField(max_length=100, blank=False, verbose_name=_('Last names'))
    aliases = models.TextField(blank=True, verbose_name=_('Aliases'), help_text=_("Other names they are known by"))
    dob = models.DateField(null=True, blank=True, verbose_name=_('Date of Birth'))
    background = models.TextField(blank=False, max_length=300, verbose_name=_('Your story'))
    family = models.TextField(blank=True, verbose_name=_('Family and associates'))
    business_activities = models.TextField(
        blank=False,
        max_length=300,
        verbose_name=_('Business Activities'))
    initial_information = models.TextField(
        max_length=150,
        blank=False,
        verbose_name=_('Where have you looked?'))

    @property
    def summary(self):
        return self.get_summary()

    def get_summary(self):
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

    def to_json(self):
        data = super(PersonTicket, self).to_json()
        data.update({
            'name': self.name,
            'surname': self.surname,
            'aliases': self.aliases,
            'dob': self.dob,
            'background': self.background,
            'family': self.family,
            'business_activities': self.business_activities,
            'initial_information': self.initial_information
        })
        return data


class CompanyTicket(Ticket):
    """ Company ownership request """
    ticket_type = 'company_ownership'
    name = models.CharField(max_length=512,
        blank=False,
        verbose_name=_('Company Name'))
    country = models.CharField(max_length=100, choices=COUNTRIES,
                             blank=False,
                             verbose_name=_('Country Registered'))
    background = models.TextField(max_length=300, blank=False, verbose_name=_('Your story'))
    sources = models.TextField(blank=False, max_length=150, verbose_name=_('Where have you looked?'))
    # story = models.TextField(blank=False, verbose_name=_('Your Story'))
    connections = models.TextField(blank=True, verbose_name=_('Connected People'))

    @property
    def summary(self):
        return self.get_summary()

    def get_summary(self):
        return "%s" % (smart_truncate(self.name, 150))

    def get_country(self):
        return dict(COUNTRIES).get(self.country, self.country)

    def most_fields(self):
        ''' Return an iterator of tuples (verbose name, display value)
        for all fields which can be shown to everybody on the ticket'''
        output = Ticket.most_fields(self)
        for i in ('name', 'country', 'background', 'sources',
                  'connections'):
            output.append((self._properties[i]._verbose_name, self.get_display_value(i)))
        return output

    def to_json(self):
        data = super(CompanyTicket, self).to_json()
        data.update({
            'name': self.name,
            'country': self.country,
            'background': self.background,
            'sources': self.sources,
            'connections': self.connections
        })
        return data


class OtherTicket(Ticket):
    """ Any other request """
    ticket_type = 'other'
    question = models.TextField(blank=False,
                                verbose_name=_('What do you want to know?'))

    @property
    def summary(self):
        return self.get_summary()

    def get_summary(self):
        words = unicode(self.question).split(" ")
        text = ""
        for word in words:
            text += word + " "
            if len(text) > 120: break
        return "%s" % text.strip()

    def to_json(self):
        data = super(OtherTicket, self).to_json()
        data.update({
            'question': self.question
        })
        return data


class TicketUpdate(models.Model, NotificationMixin):
    update_type = models.CharField(max_length=70, choices=TICKET_UPDATE_TYPES,
                                   default=TICKET_UPDATE_TYPES[0][0])
    author = models.ForeignKey(AUTH_USER_MODEL, blank=False)  # either requester, or responder
    ticket = models.ForeignKey(Ticket, blank=False)
    created = models.DateTimeField(default=datetime.datetime.now, null=False)
    comment = models.TextField()
    is_removed = models.BooleanField(default=False)

    def save(self):
        super(TicketUpdate, self).save()
        self.notify(u"%s updated ticket %s: %s" % (self.author, self.ticket.summary, self.update_type), self.author, 'ticket_details', {'ticket_id': self.ticket.pk}, 'update')

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
    paid_status = models.CharField(max_length=70, choices=PAID_STATUS, default='unpaid', blank=False)

    # when the charge was created
    created = models.DateTimeField(default=datetime.datetime.now, null=False)

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
