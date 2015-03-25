from django.contrib.auth.models import AnonymousUser#, User
from django.contrib.auth import get_user_model # as per https://docs.djangoproject.com/en/dev/topics/auth/customizing/#referencing-the-user-model
from django.test import TestCase, RequestFactory


class UserRegistration(TestCase):
	def setUp(self):
		pass

	def test_register_user(self):
		"""Test registering for an account"""
		pass

	def test_signin(self):
		"""Test signing in to an account"""
		pass

	def test_logout(self):
		"""Test logging out"""
		pass

	def test_settings(self):
		"""Test changing user profile settings"""
		pass


class DatabaseLookup(TestCase):
	def setUp(self):
		pass

	def test_select_country(self):
		"""Select a country from the country list"""
		pass


class ExpertTickets(TestCase):
	def setUp(self):
		pass

	def test_create_person_ticket(self):
		pass

	def test_create_business_ticket(self):
		pass

	def test_create_other_ticket(self):
		pass

	def test_mark_ticket_done(self):
		pass



