from core.tests import UserTestCase


class ProfileFunctions(UserTestCase):
    def test_name_fetching(self):
        self.normal_user.get_full_name()
        self.normal_user.display_name
        self.normal_user.get_short_name()

    def test_email_user(self):
        self.normal_user.email_user('test', 'test')

    def test_get_notifications(self):
        self.normal_user.get_notifications()

    def test_tickets(self):
        o = self.normal_user.tickets_assigned_open()
        c = self.normal_user.tickets_assigned_closed()
        self.assertEqual(self.normal_user.tickets_assigned_total(), o+c)

        self.normal_user.tickets_average_resolution_time()
        self.normal_user.tickets_average_resolution_time_last_30()
