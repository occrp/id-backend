from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.core.mail import send_mail
from core.mixins import *
from core.models import notification_channel_format, channel_components
from core.countries import COUNTRIES
from id.constdata import REQUESTER_TYPES, REQUEST_TYPES
from ticket.constants import *
from ticket.models import TicketCharge
from settings.settings import LANGUAGES, AUTH_USER_MODEL
from django.utils import timezone
from datetime import timedelta
import logging
logger = logging.getLogger(__name__)


class Network(models.Model):
    short_name = models.CharField(max_length=50)
    long_name = models.CharField(max_length=100, blank=True)

    def get_payment_total(self):
        total = 0
        for t in TicketCharge.objects.filter(ticket__requester__network=self):
            total += t.cost
        return total

    def __unicode__(self):
        if self.long_name:
            return "%s - %s" % (self.short_name, self.long_name)
        return self.short_name


class Center(models.Model):
    short_name = models.CharField(max_length=50)
    long_name = models.CharField(max_length=100, blank=True)
    networks = models.ManyToManyField(Network)

    def __unicode__(self):
        if self.long_name:
            return "%s - %s" % (self.short_name, self.long_name)
        return self.short_name


######## User profiles #################
# managing the profiles
class ProfileManager(NotificationMixin, BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, is_staff, is_superuser, **extra_fields):
        """
        Creates and saves a User with the given email and password.
        """
        now = timezone.now()
        if not email:
            raise ValueError('The email field has to be set.')
        email = self.normalize_email(email)
        user = self.model(email=email, is_staff=is_staff, is_active=True,
                          is_superuser=is_superuser, date_joined=now,
                          **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, is_superuser=False,
                    is_staff=False, **extra_fields):
        u = self._create_user(email, password, is_staff, is_superuser,
                                 **extra_fields)
        self.notify("New user %s." % (u), urlname="profile", params={"pk": u.pk}, action="add")
        return u

    def create_superuser(self, email, password, **extra_fields):
        u = self._create_user(email, password, True, True,
                                 **extra_fields)
        self.notify("New superuser %s." % (u), urlname="profile", params={"pk": u.pk}, action="addsuperuser")
        return u


# our own User model replacement
# as per http://stackoverflow.com/questions/20415627/how-to-properly-extend-django-user-model
class Profile(AbstractBaseUser, NotificationMixin, PermissionsMixin):

    email = models.EmailField(_('E-mail Address'), max_length=254, unique=True, blank=False)

    user_created = models.DateTimeField(auto_now_add=True)
    profile_updated = models.DateTimeField(auto_now=True)
    last_seen = models.DateTimeField(auto_now=True)

    first_name = models.CharField(max_length=64, verbose_name=_("First Name"))
    last_name = models.CharField(max_length=64, verbose_name=_("Last Name"))
    admin_notes = models.TextField(blank=True, verbose_name=_("Admin Notes"))
    locale = models.CharField(blank=True, max_length=16, choices=LANGUAGES)

    requester_type = models.CharField(blank=True, max_length=16, choices=REQUESTER_TYPES,
                                      verbose_name=_('Requester Type'))
    findings_visible = models.BooleanField(default=False,
                                      verbose_name=_('Findings Public'))

    is_user = models.BooleanField(default=True, db_index=True)
    is_staff = models.BooleanField(default=False, db_index=True)
    is_volunteer = models.BooleanField(default=False, db_index=True)
    is_active   = models.BooleanField(default=True)
    date_joined = models.DateTimeField(_('Date Joined'), default=timezone.now)

    network = models.ForeignKey(Network, null=True, blank=True, related_name='members')
    phone_number = models.CharField(blank=True, max_length=24)
    organization_membership = models.CharField(blank=True, max_length=64)
    notes = models.TextField(blank=True)
    address = models.CharField(blank=True, max_length=128)
    city = models.CharField(blank=True, max_length=64)
    province = models.CharField(blank=True, max_length=64)
    postal_code = models.CharField(blank=True, max_length=24)
    country = models.CharField(blank=True, max_length=32, choices=COUNTRIES)

    # Requester fields
    industry = models.CharField(blank=True, max_length=32, choices=INDUSTRY_TYPES)
    industry_other = models.CharField(blank=True, max_length=256)
    media = models.CharField(blank=True, max_length=64, choices=MEDIA_TYPES)
    circulation = models.CharField(blank=True, max_length=64, choices=CIRCULATION_TYPES)
    title = models.CharField(blank=True, max_length=256) # because 'Controleur des finances publiques / lutte contre la frise fiscale'...

    # Volunteer fields
    interests = models.TextField(blank=True)
    expertise = models.TextField(blank=True)
    languages = models.TextField(blank=True)
    availability = models.TextField(blank=True)
    databases = models.TextField(blank=True)
    conflicts = models.TextField(blank=True)

    # Django auth module settings
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    # object manager
    objects = ProfileManager()

    def get_full_name(self):
        return self.display_name

    def get_short_name(self):
        return self.first_name

    def email_user(self, subject, message, from_email=None, **kwargs):
        logger.info("E-mailed user %s with subject '%s'" % (self.email, subject))
        send_mail(subject, message, from_email, [self.email], **kwargs)

    def get_notifications(self, start=0, count=10):
        return self.notification_set.all()[start:count]

    def unseen_notifications_count(self):
        return self.notification_set.filter(is_seen=False).count()

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

    def groups_display(self):
        return ', '.join(x.capitalize() for x in ['user', 'staff', 'volunteer', 'superuser'] if getattr(self, 'is_%s' % x))


    @property
    def num_requests(self):
        # XXX beware, this is expensive!
        if not tickets_per_user:
            set_ticket_counts()
        return tickets_per_user[self.key]

    @property
    def display_name(self):
        if self.first_name or self.last_name:
            return u" ".join((self.first_name, self.last_name))
        return self.email or u''

    @property
    def is_approved(self):
        return any((
            self.is_user, self.is_staff, self.is_volunteer, self.is_superuser
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
        if self.is_staff or self.is_superuser or self.is_user:
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
        return unicode(self.display_name)

    def __str__(self):
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

    def tickets_assigned_open(self):
        return self.tickets_responded.filter(status__in=['new', 'in-progress']).count()

    def tickets_assigned_closed(self):
        return self.tickets_responded.filter(status__in=['closed']).count()

    def tickets_assigned_total(self):
        return self.tickets_assigned_open() + self.tickets_assigned_closed()

    def tickets_get_set(self, _max=None):
        res = self.tickets_responded.filter(status__in=['closed'])
        if _max:
            res = res[:_max]
        return res

    def tickets_average_resolution_time_calculate(self, tot):
        if len(tot) > 0:
            times = [x.resolution_time() for x in tot]
            average_timedelta = sum(times, timedelta(0)) / len(times)
            return average_timedelta
        else:
            return timedelta(0)

    def tickets_average_resolution_time_last_30(self):
        if (self.tickets_assigned_total() == 0):
            return timedelta(days=0)

        tot = self.tickets_get_set(30)
        return self.tickets_average_resolution_time_calculate(tot)

    def tickets_average_resolution_time(self):
        if (self.tickets_assigned_total() == 0):
            return timedelta(days=0)

        tot = self.tickets_get_set()
        return self.tickets_average_resolution_time_calculate(tot)

    def notifications_subscribe(self, channel):
        assert(notification_channel_format.match(channel))
        ns = NotificationSubscription()
        ns.user = self
        ns.set_channel(channel)
        ns.save()
        return True

    def notifications_unsubscribe(self, channel):
        assert(notification_channel_format.match(channel))
        components = channel_components(channel)
        subscriptions = NotificationSubscription.objects.filter(**components)
        count = subscriptions.count()
        subscriptions.delete()
        return count

    def to_json(self):
        return {"id": self.id, "email": self.email}

    def save(self, *args, **kw):
        import traceback

        ## FIXME: Temporary fix to make users stop being locked out
        try:
            u = Profile.objects.get(id=self.id)
            if u.is_active and not self.is_active:
                self.is_active = u.is_active
            if u.is_user and not self.is_user:
                self.is_user = u.is_user
        except Profile.DoesNotExist:
            pass
        #####################################################################

        logger.info("Saving profile for user %s: {is_active:%s, is_user:%s, is_volunteer:%s, is_staff:%s, is_superuser:%s}" % (self.email, self.is_active, self.is_user, self.is_volunteer, self.is_staff, self.is_superuser))
        if self.pk is not None:
            try:
                orig = Profile.objects.get(pk=self.pk)
                if orig.network != self.network:
                    self.notify("User %s changed network from %s to %s" % (self, orig.network, self.network), urlname="profile", params={"pk": self.pk}, action="update")
                if orig.is_superuser != self.is_superuser:
                    self.notify("User %s admin status changed to %s" % (self, self.is_superuser), urlname="profile", params={"pk": self.pk}, action="update")
            except Profile.DoesNotExist:
                pass

        else:
            if len(Profile.objects.filter(email=self.email)) > 0:
                raise Exception("Cannot create duplicate user!")

        return super(Profile, self).save(*args, **kw)

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        abstract = False
        swappable = 'AUTH_USER_MODEL'


######## Account management ############
class AccountRequest(models.Model, DisplayMixin):
    request_type = models.CharField(blank=False, max_length=64, choices=REQUEST_TYPES)
    user = models.ForeignKey(AUTH_USER_MODEL, blank=False)
    approved = models.NullBooleanField(default=None, blank=True, null=True, verbose_name=_('Approved'))
    date_created = models.DateTimeField(auto_now_add=True,
                                        verbose_name=_('Date Created'))

    # temporary fix for updated profiles
    already_updated = models.BooleanField(default=False)

    GROUPS = []
    MAIL_TEMPLATE = 'accountrequest/mail_notification.jinja'

    def __str__(self):
        return "%s:%s:%s:%s" % (self.user, self.request_type, self.approved, self.date_created)

    class Meta:
        ordering = ['request_type', 'approved', 'date_created']
        unique_together = (('user', 'request_type'),)

    def get_display_value(self, property_name):
        if property_name != 'approved':
            return super(AccountRequest, self).get_display_value(property_name)
        else:
            return ('--' if self.approved is None
                    else _('Yes') if self.approved is True
                    else _('No'))

    def approve(self):
        """
        Adds the Account Request's email address to the appropriate Google
        groups, and marks the request as approved.
        """
        if self.request_type == 'volunteer':
            self.user.is_volunteer = True
            self.user.save()
        elif self.request_type == 'request':
            self.user.is_user = True
            self.user.save()

        self.approved = True
        self.save()
        self.notify_approved()

    def reject(self):
        """
        Removes the user from the group!
        """
        if self.request_type == 'volunteer':
            self.user.is_volunteer = False
            self.user.save()
        elif self.request_type == 'request':
            self.user.is_user = False
            self.user.save()

        self.approved = False
        self.save()
        self.notify_rejected()

    def notify_received(self):
        self.email_notification(
            to=self.user.email,
            subject=unicode(_('Your Account Request was received')),
            template='mail/account_request/received.jinja',
            context={'request': self}
        )
        for admin in AUTH_USER_MODEL.objects.filter(is_superuser=True):
            with templocale(admin.locale or 'en'):
                self.email_notification(
                    to=admin.email,
                    subject=unicode(_('An Account Request was received')),
                    template='mail/account_request/received_admin.jinja',
                    context={'request': self}
                )

    def notify_approved(self):
        self.email_notification(
            to=self.user.email,
            subject=unicode(_('An update to your Account Request')),
            template='mail/account_request/approved.jinja',
            context={'request': self}
        )

    def notify_rejected(self):
        self.email_notification(
            to=self.user.email,
            subject=unicode(_('Your Account Request was rejected')),
            template='mail/account_request/rejected.jinja',
            context={'request': self}
        )

    def email_notification(self, to, subject, template, context):
        pass


class DatabaseScrapeRequest(models.Model):
    url = models.URLField(blank=False, verbose_name=_("URL"))
    name = models.CharField(max_length=200, verbose_name=_("Name"))
    description = models.TextField(verbose_name=_("Description"))
    # plusones = models.ManyToManyField(AUTH_USER_MODEL)

    # def plusone(self, user):
    #    self.plusone.add(user)

    #def minusone(self, user):
    #    self.plusone.remove(user)


class Feedback(models.Model):
    name = models.CharField(blank=False, max_length=100)
    email = models.EmailField(blank=False)
    timestamp = models.DateTimeField(auto_now_add=True)
    message = models.TextField()

    def __unicode__(self):
        return u"From: %s <%s>\nDate: %s\n\n%s\n" % (self.name, self.email,
            self.timestamp, self.message)

    #def save(self):
    #    self.notify("Received feedback from %s." % (self.name), action="add")
    #    super(Feedback, self).save()
    #    # Send e-mail!
