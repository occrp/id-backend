from django.contrib.auth.models import AbstractUser
from django.db import models

from .countries import COUNTRIES


class Profile(AbstractUser):
    class Meta:
        db_table = 'accounts_profile'

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

