from django.test import TestCase
from core.tests import UserTestCase
from core.testclient import TestClient
from settings.settings import *
from django.core.urlresolvers import reverse
from ticket.models import *

class TicketsTest(UserTestCase):
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

    def test_join_and_leave_ticket_as_volunteer(self):
        client = TestClient()
        client.login_user(self.volunteer_user)
        t = OtherTicket()
        t.requester = self.normal_user
        t.save()
        response = client.post(reverse('ticket_join', kwargs={"pk": t.id}), {})
        t = OtherTicket.objects.get(id=t.id)
        self.assertIn(self.volunteer_user, t.volunteers.all())
        response = client.post(reverse('ticket_leave', kwargs={"pk": t.id}), {})
        t = OtherTicket.objects.get(id=t.id)
        self.assertNotIn(self.volunteer_user, t.volunteers.all())

    def test_edit_ticket(self):
        pass

    def test_ticket_settings(self):
        pass

    def test_close_ticket(self):
        pass

    def test_reopen_ticket(self):
        pass
