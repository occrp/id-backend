from django.test import TestCase

from core.tests import UserTestCase


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


class ProfileFunctions(UserTestCase):
        def test_name_fetching(self):
                self.normal_user.get_full_name()
                self.normal_user.display_name
                self.normal_user.get_short_name()

        def test_email_user(self):
                self.normal_user.email_user('test', 'test')

        def test_get_notifications(self):
                self.normal_user.get_notifications()

        def test_group_memberships(self):
                self.normal_user.groups_display()

        def test_permissions(self):
                self.normal_user.is_approved

        def test_tickets(self):
                o = self.normal_user.tickets_assigned_open()
                c = self.normal_user.tickets_assigned_closed()
                self.assertEqual(self.normal_user.tickets_assigned_total(), o+c)

                self.normal_user.tickets_average_resolution_time()
                self.normal_user.tickets_average_resolution_time_last_30()
