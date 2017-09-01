from django.test import TestCase
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser


class ProfileFunctions(TestCase):

    def setUp(self):
        user_model = get_user_model()

        self.anonymous_user = AnonymousUser()
        self.normal_user = user_model.objects.create_user(
            'testuser@occrp.org', password='top_secret')
        self.staff_user = user_model.objects.create_user(
            'teststaff@occrp.org', password='top_secret', is_staff=True)
        self.admin_user = user_model.objects.create_user(
            'testsuperuser@occrp.org', password='top_secret', is_superuser=True)

    def test_tickets(self):
        o = self.normal_user.tickets_assigned_open()
        c = self.normal_user.tickets_assigned_closed()
        self.assertEqual(self.normal_user.tickets_assigned_total(), o+c)

        self.normal_user.tickets_average_resolution_time()
        self.normal_user.tickets_average_resolution_time_last_30()
