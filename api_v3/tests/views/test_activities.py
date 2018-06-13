import json

from api_v3.factories import ProfileFactory, TicketFactory, AttachmentFactory
from api_v3.models import Action
from .support import TestCase, APIClient, reverse


class ActivitiesEndpointTestCase(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.users = [
            ProfileFactory.create(),
            ProfileFactory.create()
        ]
        self.tickets = [
            TicketFactory.create(requester=self.users[1])
        ]
        self.attachments = [
            AttachmentFactory.create(
                user=self.users[0], ticket=self.tickets[0])
        ]
        self.activities = [
            Action.objects.create(
                actor=self.users[1],
                target=self.tickets[0],
                action=self.attachments[0],
                verb='test-action'
            )
        ]

    def test_list_anonymous(self):
        response = self.client.get(reverse('action-list'))

        self.assertEqual(response.status_code, 401)

    def test_list_authenticated_no_tickets(self):
        self.client.force_authenticate(self.users[0])

        response = self.client.get(reverse('action-list'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content)['data'], [])

    def test_list_authenticated(self):
        self.client.force_authenticate(self.users[1])

        response = self.client.get(reverse('action-list'))

        self.assertEqual(response.status_code, 200)
        self.assertIn(self.activities[0].verb, response.content)
        self.assertIn('last-id', response.content)
        self.assertIn('first-id', response.content)

    def test_list_authenticated_with_includes(self):
        self.client.force_authenticate(self.users[1])

        response = self.client.get(
            reverse('action-list'), {'include': 'attachment'})

        self.assertEqual(response.status_code, 200)
        self.assertIn('included', response.content)
