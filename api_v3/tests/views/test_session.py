import json

from django.conf import settings

from api_v3.factories import ProfileFactory, TicketFactory
from api_v3.serializers import ProfileSerializer
from .support import TestCase, APIClient, reverse


class SessionsEndpointTestCase(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.users = [
            ProfileFactory.create(),
            ProfileFactory.create(is_superuser=True)
        ]

        self.tickets = [
            TicketFactory.create(requester=self.users[0]),
            TicketFactory.create(requester=self.users[1])
        ]

    def test_me_anonymous(self):
        response = self.client.get(reverse('me-list'))

        self.assertEqual(response.status_code, 401)

    def test_me_authenticated(self):
        self.client.force_authenticate(self.users[0])

        response = self.client.get(reverse('me-list'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.data,
            ProfileSerializer(self.users[0]).data
        )

        body = json.loads(response.content)

        self.assertEqual(body['data']['attributes']['tickets-count'], 1)
        self.assertEqual(
            body['meta'],
            {
                'member-centers': sorted(settings.MEMBER_CENTERS),
                'expense-scopes': sorted(settings.EXPENSE_SCOPES)
            }
        )

    def test_me_authenticated_superuser(self):
        self.client.force_authenticate(self.users[1])

        response = self.client.get(reverse('me-list'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.data,
            ProfileSerializer(self.users[1]).data
        )

        body = json.loads(response.content)

        self.assertEqual(body['data']['attributes']['tickets-count'], 2)
