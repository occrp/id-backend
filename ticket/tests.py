import unittest

from django.test import TestCase
from core.testclient import TestClient
# from settings.settings import *
from django.core.urlresolvers import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser

from ticket.models import PersonTicket, CompanyTicket, OtherTicket
from ticket.models import TicketUpdate


@unittest.skip('Disabled')
class TicketsTest(TestCase):

    def setUp(self):
        user_model = get_user_model()

        self.anonymous_user = AnonymousUser()
        self.normal_user = user_model.objects.create_user(
            'testuser@occrp.org', password='top_secret')
        self.staff_user = user_model.objects.create_user(
            'teststaff@occrp.org', password='top_secret', is_staff=True)
        self.admin_user = user_model.objects.create_user(
            'testsuperuser@occrp.org', password='top_secret', is_superuser=True)

    def test_create_person_ticket(self):
        client = TestClient()
        client.login_user(self.normal_user)

        dset = {}
        dset["ticket_type-ticket_type"] = "person_ownership"
        dset["person-name"] = "James"
        dset["person-surname"] = "Robb"
        dset["person-aliases"] = "James The Rake\nSonny Jim"
        dset["person-background"] = "Eats doughnuts and drinks cocoa. Has been known to dance with wolves."
        dset["person-family"] = "Nonni  Dordingull  partner\nSvampur    Sveinsson   secretary"
        dset["person-business_activities"] = "Buys and sells goat meat. Runs the Goat Meat and Truffle Discount Emporium."
        dset["person-dob"] = "1980-07-16"
        dset["person-initial_information"] = "The Internet"
        dset["person-deadline"] = "2015-01-14"
        dset["person-sensitive"] = "on"
        dset["company-name"] = ""
        dset["company-country"] = ""
        dset["company-background"] = ""
        dset["company-sources"] = ""
        dset["company-story"] = ""
        dset["company-connections"] = ""
        dset["company-deadline"] = ""
        dset["other-question"] = ""
        dset["other-deadline"] = ""

        response = client.post(reverse('ticket_submit'), dset)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(PersonTicket.objects.count() == 1)

    def test_create_company_ticket(self):
        client = TestClient()
        client.login_user(self.normal_user)

        dset = {}
        dset["ticket_type-ticket_type"] = "company_ownership"
        dset["person-name"] = ""
        dset["person-aliases"] = ""
        dset["person-background"] = ""
        dset["person-biography"] = ""
        dset["person-family"] = ""
        dset["person-business_activities"] = ""
        dset["person-dob"] = ""
        dset["person-birthplace"] = ""
        dset["person-initial_information"] = ""
        dset["person-location"] = ""
        dset["person-deadline"] = ""
        dset["company-sensitive"] = "on"
        dset["company-name"] = "Mango Corp"
        dset["company-country"] = "IS"
        dset["company-background"] = "Unknown"
        dset["company-sources"] = "Companies House"
        dset["company-story"] = "Some story"
        dset["company-connections"] = ""
        dset["company-deadline"] = "2015-03-12"
        dset["other-deadline"] = ""
        dset["other-sensitive"] = ""
        dset["other-question"] = ""

        response = client.post(reverse('ticket_submit'), dset)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(CompanyTicket.objects.count() == 1)

    def test_create_other_ticket(self):
        client = TestClient()
        client.login_user(self.normal_user)

        dset = {}
        dset["ticket_type-ticket_type"] = "other"
        dset["person-name"] = ""
        dset["person-aliases"] = ""
        dset["person-background"] = ""
        dset["person-biography"] = ""
        dset["person-family"] = ""
        dset["person-business_activities"] = ""
        dset["person-dob"] = ""
        dset["person-birthplace"] = ""
        dset["person-initial_information"] = ""
        dset["person-location"] = ""
        dset["person-deadline"] = ""
        dset["company-name"] = ""
        dset["company-country"] = ""
        dset["company-background"] = ""
        dset["company-sources"] = ""
        dset["company-story"] = ""
        dset["company-connections"] = ""
        dset["company-deadline"] = ""
        dset["other-deadline"] = "2015-1-14"
        dset["other-sensitive"] = "on"
        dset["other-question"] = "I am asking you a question"

        response = client.post(reverse('ticket_submit'), dset)

        self.assertEqual(response.status_code, 302)
        self.assertTrue(OtherTicket.objects.count() == 1)

    def test_add_comment(self):
        t, created = OtherTicket.objects.get_or_create(requester=self.normal_user)
        client = TestClient()
        client.login_user(self.normal_user)

        dset = {"comment": "Hello comment"}
        response = client.post(reverse('ticket_details', kwargs={"ticket_id": t.id}), dset)

        self.assertEqual(response.status_code, 302)
        self.assertTrue(TicketUpdate.objects.count() == 1)

    def test_join_and_leave_ticket_as_staff(self):
        client = TestClient()
        client.login_user(self.staff_user)
        t = OtherTicket()
        t.requester = self.normal_user
        t.save()
        response = client.post(reverse('ticket_join', kwargs={"pk": t.id}), {})
        t = OtherTicket.objects.get(id=t.id)
        self.assertIn(self.staff_user, t.responders.all())
        response = client.post(reverse('ticket_leave', kwargs={"pk": t.id}), {})
        t = OtherTicket.objects.get(id=t.id)
        self.assertNotIn(self.staff_user, t.responders.all())

    def test_edit_ticket(self):
        pass

    def test_ticket_settings(self):
        pass

    def test_close_ticket(self):
        pass

    def test_reopen_ticket(self):
        pass

    def test_ticket_list_all_open_authorized(self):
        client = TestClient()
        client.login_user(self.staff_user)
        r = client.get(reverse('ticket_all_open_list'))
        self.assertEqual(r.status_code, 200)
        # print r.status_code, r.content

    def test_ticket_list_all_closed_authorized(self):
        client = TestClient()
        client.login_user(self.staff_user)
        r = client.get(reverse('ticket_all_closed_list'))
        self.assertEqual(r.status_code, 200)
        # r.content

    def test_ticket_my_open_list_unauthorized(self):
        client = TestClient()
        r = client.get('ticket_list')
        # self.assertEqual(r.status_code, 403)
        #print r.status_code, r.content

    def test_ticket_my_open_list_authorized(self):
        client = TestClient()
        client.login_user(self.staff_user)
        r = client.get(reverse('ticket_list'))
        self.assertEqual(r.status_code, 200)
        # print r.status_code, r.content

    def test_ticket_list_my_closed_authorized(self):
        client = TestClient()
        client.login_user(self.staff_user)
        r = client.get(reverse('ticket_closed_list'))
        self.assertEqual(r.status_code, 200)
        # r.content

    def test_ticket_list_my_assigned_authorized(self):
        client = TestClient()
        client.login_user(self.staff_user)
        r = client.get(reverse('ticket_assigned_list'))
        self.assertEqual(r.status_code, 200)
        # r.content

    def test_ticket_list_my_assigned_closed_authorized(self):
        client = TestClient()
        client.login_user(self.staff_user)
        r = client.get(reverse('ticket_assigned_closed_list'))
        self.assertEqual(r.status_code, 200)
        # r.content

    def test_ticket_list_public_open_authorized(self):
        client = TestClient()
        client.login_user(self.staff_user)
        r = client.get(reverse('ticket_public_list'))
        self.assertEqual(r.status_code, 200)
        # r.content

    def test_ticket_list_public_closed_authorized(self):
        client = TestClient()
        client.login_user(self.staff_user)
        r = client.get(reverse('ticket_public_closed_list'))
        self.assertEqual(r.status_code, 200)
        # r.content

    def test_ticket_list_unassigned_authorized(self):
        client = TestClient()
        client.login_user(self.staff_user)
        r = client.get(reverse('ticket_unassigned_list'))
        self.assertEqual(r.status_code, 200)
        # r.content

    def test_ticket_list_deadline_authorized(self):
        client = TestClient()
        client.login_user(self.staff_user)
        r = client.get(reverse('ticket_deadline_list'))
        self.assertEqual(r.status_code, 200)
        # r.content

    def test_ticket_assign_unassign(self):
        client = TestClient()
        client.login_user(self.admin_user)
        t = OtherTicket()
        t.requester = self.normal_user
        t.save()

        t_assign = reverse('ticket_assign', kwargs={'pk': t.id})
        t_unassign = reverse('ticket_unassign', kwargs={'pk': t.id})

        # Try assigning a staff member
        r = client.post(t_assign, {'user': self.staff_user.id})
        self.assertEqual(r.status_code, 200)
        # print r.content

        # Try assigning a staff member
        r = client.post(t_unassign, {'user': self.staff_user.id})
        self.assertEqual(r.status_code, 200)
        # print r.content
