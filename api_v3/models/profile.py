from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models

from .countries import COUNTRIES


class ProfileManager(UserManager):

    def _create_user(self, email, password, **extra_fields):
        """
        Creates and saves a User with the given email and password.
        """
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)


class Profile(AbstractUser):
    class Meta:
        db_table = 'accounts_profile'

    objects = ProfileManager()

    # Disable the `username` field
    username = None

    profile_updated = models.DateTimeField(auto_now=True)
    email = models.EmailField(max_length=254, unique=True, blank=False)
    first_name = models.CharField(max_length=64)
    last_name = models.CharField(max_length=64)
    locale = models.CharField(blank=True, max_length=16)
    phone_number = models.CharField(blank=True, max_length=255)
    organization = models.CharField(blank=True, max_length=1024)
    country = models.CharField(blank=True, max_length=32, choices=COUNTRIES)
    bio = models.TextField(blank=True, null=True)

    # Django auth module settings
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    @property
    def display_name(self):
        if self.first_name or self.last_name:
            return u' '.join((self.first_name, self.last_name)).strip()
        return self.email

    def get_full_name(self):
        return self.display_name
