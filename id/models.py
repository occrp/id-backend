from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from id.mixins import *
from id.constdata import *
from ticket.constants import *
from ticket.models import TicketCharge
from settings.settings import LANGUAGES, AUTH_USER_MODEL
from django.utils import timezone

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


######## User profiles #################

# managing the profiles
class ProfileManager(BaseUserManager):
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
                          is_superuser=is_superuser, date_joined=now, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        return self._create_user(email, password, False, False,
                                 **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        print(email)
        return self._create_user(email, password, True, True,
                                 **extra_fields)
      
# our own User model replacement
# as per http://stackoverflow.com/questions/20415627/how-to-properly-extend-django-user-model
#
class Profile(AbstractBaseUser, PermissionsMixin):
    
    email = models.EmailField(_('E-mail Address'), max_length=254, unique=True, blank=False)

    user_created = models.DateTimeField(auto_now_add=True)
    profile_updated = models.DateTimeField(auto_now=True)
    last_seen = models.DateTimeField(auto_now=True)

    first_name = models.CharField(max_length=64, verbose_name=_("First Name"))
    last_name = models.CharField(max_length=64, verbose_name=_("Last Name"))
    abbr = models.CharField(max_length=8, blank=True, null=True, unique=True, verbose_name=_("Initials"))
    admin_notes = models.TextField(blank=True, verbose_name=_("Admin Notes"))
    locale = models.CharField(blank=True, max_length=16, choices=LANGUAGES)

    requester_type = models.CharField(blank=True, max_length=16, choices=REQUESTER_TYPES,
                                      verbose_name=_('Requester Type'))
    findings_visible = models.BooleanField(default=False,
                                      verbose_name=_('Findings Public'))

    is_user = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=True)
    is_volunteer = models.BooleanField(default=False)
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
    industry_other = models.CharField(blank=True, max_length=96)
    media = models.CharField(blank=True, max_length=64, choices=MEDIA_TYPES)
    circulation = models.CharField(blank=True, max_length=64, choices=CIRCULATION_TYPES)
    title = models.CharField(blank=True, max_length=96) # because 'Controleur des finances publiques / lutte contre la frise fiscale'...

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
        return self.display_name()

    def get_short_name(self):
        return self.first_name

    def email_user(self, subject, message, from_email=None, **kwargs):
        send_mail(subject, message, from_email, [self.email], **kwargs)
    

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
        return self.email or ''

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

    def to_json(self):
        return {"id": self.id, "email": self.email}

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        abstract = False
        swappable = 'AUTH_USER_MODEL'
        #index_name = "userprofile_staff"
        #index_name_all = "userprofile_all"
        #search_fields = ['name', 'email', 'full_name']
        #fields = (('email', 'display_name', 'admin_notes',
        #          'requester_type', 'findings_visible'
        #          'is_superuser', 'is_staff', 'is_volunteer', 'is_user'
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

######## Account management ############
class AccountRequest(models.Model, DisplayMixin):
    request_type = models.CharField(blank=False, max_length=64, choices=REQUEST_TYPES)
    user = models.ForeignKey(AUTH_USER_MODEL, blank=False)
    approved = models.BooleanField(default=None, blank=True, verbose_name=_('Approved'))
    date_created = models.DateTimeField(auto_now_add=True,
                                        verbose_name=_('Date Created'))

    # temporary fix for updated profiles
    already_updated = models.BooleanField(default=False)

    GROUPS = []
    MAIL_TEMPLATE = 'accountrequest/mail_notification.jinja'

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
            self.user.is_volunteer = True()
            self.user.save()
        elif self.request_type == 'requester':
            self.user.is_user = True()
            self.user.save()

        self.approved = True
        self.save()
        self.notify_approved()

    def reject(self):
        """
        Removes the user from the group!
        """
        self.approved = False
        self.save()
        self.notify_rejected()

    def notify_received(self):
        email_notification(
            to=self.user.email,
            subject=unicode(_('Your Account Request was received')),
            template='mail/account_request/received.jinja',
            context={'request': self}
        )
        for admin in AUTH_USER_MODEL.objects.filter(is_superuser=True):
            with templocale(admin.locale or 'en'):
                email_notification(
                    to=admin.email,
                    subject=unicode(_('An Account Request was received')),
                    template='mail/account_request/received_admin.jinja',
                    context={'request': self}
                )

    def notify_approved(self):
        email_notification(
            to=self.user.email,
            subject=unicode(_('An update to your Account Request')),
            template='mail/account_request/approved.jinja',
            context={'request': self}
        )

    def notify_rejected(self):
        email_notification(
            to=self.user.email,
            subject=unicode(_('Your Account Request was rejected')),
            template='mail/account_request/rejected.jinja',
            context={'request': self}
        )

class DatabaseScrapeRequest(models.Model):
    url = models.URLField(blank=False, verbose_name=_("URL"))
    name = models.CharField(max_length=200, verbose_name=_("Name"))
    description = models.TextField(verbose_name=_("Description"))
    # plusones = models.ManyToManyField(AUTH_USER_MODEL)

    # def plusone(self, user):
    #    self.plusone.add(user)

    #def minusone(self, user):
    #    self.plusone.remove(user)

