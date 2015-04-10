from django.test import TestCase
from django.contrib.auth.models import AnonymousUser#, User
from django.contrib.auth import get_user_model # as per https://docs.djangoproject.com/en/dev/topics/auth/customizing/#referencing-the-user-model

class UserTestCase(TestCase):
    def setUp(self):
        self.anonymous_user = AnonymousUser()
        
        self.normal_user = get_user_model().objects.create_user(
            email='testuser@occrp.org', password='top_secret')
        self.normal_user.is_user = True
        self.normal_user.save()

        self.volunteer_user = get_user_model().objects.create_user(
            email='testvolunteer@occrp.org', password='top_secret')
        self.volunteer_user.is_volunteer = True
        self.volunteer_user.save()

        self.staff_user = get_user_model().objects.create_user(
            email='teststaff@occrp.org', password='top_secret')
        self.staff_user.is_staff = True
        self.staff_user.save()

        self.admin_user = get_user_model().objects.create_user(
            email='testsuperuser@occrp.org', password='top_secret')
        self.admin_user.is_superuser = True
        self.admin_user.save()

    def tearDown(self):
        pass

