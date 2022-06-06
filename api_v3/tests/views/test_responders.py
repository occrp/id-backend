import json

from api_v3.factories import (
    ProfileFactory, TicketFactory, ResponderFactory, SubscriberFactory)
from api_v3.models import Ticket, Responder
from api_v3.serializers import ResponderSerializer
from .support import ApiTestCase, APIClient, reverse


class RespondersEndpointTestCase(ApiTestCase):

    def setUp(self):
        self.client = APIClient()
        self.users = [
            ProfileFactory.create(),
            ProfileFactory.create(),
            ProfileFactory.create(is_superuser=True),
            ProfileFactory.create(),
        ]
        self.tickets = [
            TicketFactory.create(requester=self.users[0]),
            TicketFactory.create(requester=self.users[1])
        ]
        self.responders = [
            ResponderFactory.create(ticket=self.tickets[0], user=self.users[1]),
            ResponderFactory.create(ticket=self.tickets[1], user=self.users[2])
        ]

        self.subscriber = SubscriberFactory.create(
            ticket=self.tickets[0], user=self.users[3])

    def test_create_non_superuser(self):
        self.client.force_authenticate(self.users[0])

        new_data = self.as_jsonapi_payload(
            ResponderSerializer, self.responders[0])

        new_data['data']['attributes']['user']['id'] = self.users[2].id

        response = self.client.post(
            reverse('responder-list'),
            data=json.dumps(new_data),
            content_type=self.JSON_API_CONTENT_TYPE
        )

        self.assertEqual(response.status_code, 422)

        response = json.loads(response.content)
        self.assertEqual(response['errors'][0]['detail'], 'Ticket not found.')
        self.assertEqual(
            response['errors'][0]['source']['pointer'],
            '/data/attributes/ticket'
        )

    def test_create_superuser_user_is_responder(self):
        self.client.force_authenticate(self.users[2])

        new_data = self.as_jsonapi_payload(
            ResponderSerializer, self.responders[0])

        new_data['data']['attributes']['user']['id'] = self.subscriber.user.id

        response = self.client.post(
            reverse('responder-list'),
            data=json.dumps(new_data),
            content_type=self.JSON_API_CONTENT_TYPE
        )
        self.assertEqual(response.status_code, 422)

        response = json.loads(response.content)
        self.assertEqual(
            response['errors'][0]['source']['pointer'],
            '/data/relationships/user'
        )
        self.assertEqual(
            response['errors'][0]['detail'],
            'Subscriber already exists.'
        )

    def test_create_superuser(self):
        self.client.force_authenticate(self.users[2])

        # Set to initial ticket status
        self.tickets[0].status = Ticket.STATUSES[0][0]
        self.tickets[0].save()

        responders_count = Responder.objects.count()

        new_data = self.as_jsonapi_payload(
            ResponderSerializer, self.responders[0])

        new_data['data']['attributes']['user']['id'] = self.users[0].id

        response = self.client.post(
            reverse('responder-list'),
            data=json.dumps(new_data),
            content_type=self.JSON_API_CONTENT_TYPE
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(Responder.objects.count(), responders_count + 1)
        self.assertEqual(
            Ticket.objects.get(id=self.tickets[0].id).status,
            Ticket.STATUSES[1][0]
        )

    def test_delete_non_superuser(self):
        self.client.force_authenticate(self.users[0])

        response = self.client.delete(
            reverse('responder-detail', args=[self.responders[0].id]),
            content_type=self.JSON_API_CONTENT_TYPE
        )

        self.assertEqual(response.status_code, 404)

    def test_delete_superuser(self):
        self.client.force_authenticate(self.users[2])

        responders_count = Responder.objects.count()

        response = self.client.delete(
            reverse('responder-detail', args=[self.responders[0].id]),
            content_type=self.JSON_API_CONTENT_TYPE
        )

        self.assertEqual(response.status_code, 204)
        self.assertEqual(Responder.objects.count(), responders_count - 1)

    def test_list_anonymous(self):
        response = self.client.get(reverse('responder-list'))

        self.assertEqual(response.status_code, 401)

    def test_list_authenticated(self):
        self.client.force_authenticate(self.users[0])

        response = self.client.get(reverse('responder-list'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(json.loads(response.content)['data']), 1)
        self.assertEqual(
            json.loads(response.content)['data'][0]['id'],
            str(self.responders[0].id)
        )

    def test_get_authenticated(self):
        self.client.force_authenticate(self.users[0])

        response = self.client.get(
            reverse('responder-detail', args=[self.responders[0].id]))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            json.loads(response.content)['data']['id'],
            str(self.responders[0].id)
        )

    def test_get_authenticated_without_access(self):
        self.client.force_authenticate(self.users[0])

        response = self.client.get(
            reverse('responder-detail', args=[self.responders[1].id]))

        self.assertEqual(response.status_code, 404)
