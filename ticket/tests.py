from django.contrib.auth.models import AnonymousUser#, User
from django.contrib.auth import get_user_model # as per https://docs.djangoproject.com/en/dev/topics/auth/customizing/#referencing-the-user-model
from django.test import TestCase
from core.testclient import TestClient
from settings.settings import *
from django.core.urlresolvers import reverse
from ticket.models import *

class TicketsTest(TestCase):
    def setUp(self):
        self.anonymous_user = AnonymousUser()
        self.normal_user = get_user_model().objects.create_user(
            username='requester', email='testuser@occrp.org', password='top_secret')
        self.normal_user.profile.is_user = True
        self.normal_user.profile.save()

        self.volunteer_user = get_user_model().objects.create_user(
            username='volunteer', email='testuser@occrp.org', password='top_secret')
        self.volunteer_user.profile.is_volunteer = True
        self.volunteer_user.profile.save()

        self.staff_user = get_user_model().objects.create_user(
            username='staff', email='testuser@occrp.org', password='top_secret')
        self.staff_user.profile.is_staff = True
        self.staff_user.profile.save()

        self.admin_user = get_user_model().objects.create_user(
            username='admin', email='testuser@occrp.org', password='top_secret')
        self.admin_user.is_superuser = True
        self.admin_user.save()
        self.admin_user.profile.is_admin = True
        self.admin_user.profile.save()

    def tearDown(self):
        pass

    def test_create_person_ticket(self):
        client = TestClient()
        client.login_user(self.normal_user)

        dset = {}
        dset["ticket_type-ticket_type"] = "person_ownership"
        dset["person-name"] = "James Robb"
        dset["person-aliases"] = "James The Rake\nSonny Jim"
        dset["person-background"] = "Eats doughnuts and drinks cocoa. Has been known to dance with wolves."
        dset["person-biography"] = "Born on the plains, travels in planes. Thinks almonds are good."
        dset["person-family"] = "Nonni  Dordingull  partner\nSvampur    Sveinsson   secretary"
        dset["person-business_activities"] = "Buys and sells goat meat. Runs the Goat Meat and Truffle Discount Emporium."
        dset["person-dob"] = "1980-7-16"
        dset["person-birthplace"] = "Kanuckistan"
        dset["person-initial_information"] = "The Internet"
        dset["person-location"] = "Sarajevo"
        dset["person-deadline"] = "2015-1-14"
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

    def test_join_ticket(self):
        pass

    def test_leave_ticket(self):
        pass

    def test_edit_ticket(self):
        pass

    def test_ticket_settings(self):
        pass

    def test_close_ticket(self):
        pass

    def test_reopen_ticket(self):
        pass
