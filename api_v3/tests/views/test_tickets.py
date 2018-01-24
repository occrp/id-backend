import json

from api_v3.models import Ticket, Action
from api_v3.factories import (
    ProfileFactory,
    ResponderFactory,
    TicketFactory
)
from api_v3.serializers import TicketSerializer
from .support import ApiTestCase, APIClient, reverse


class TicketsEndpointTestCase(ApiTestCase):

    def setUp(self):
        self.client = APIClient()
        self.users = [
            ProfileFactory.create(),
            ProfileFactory.create(),
            ProfileFactory.create(),
            ProfileFactory.create(),
        ]

        self.tickets = [
            TicketFactory.create(requester=self.users[0]),
            TicketFactory.create(requester=self.users[0]),
            TicketFactory.create(requester=self.users[1])
        ]

        self.responders = [
            ResponderFactory.create(
                ticket=self.tickets[0], user=self.users[1]),
            ResponderFactory.create(
                ticket=self.tickets[0], user=self.users[2])
        ]

    def test_list_anonymous(self):
        response = self.client.get(reverse('ticket-list'))

        self.assertEqual(response.status_code, 403)

    def test_list_authenticated(self):
        self.client.force_authenticate(self.users[0])

        response = self.client.get(reverse('ticket-list'))

        self.assertEqual(response.status_code, 200)
        self.assertIn(self.tickets[0].background, response.content)

        body = json.loads(response.content)

        self.assertEqual(body['meta']['total']['all'], 2)

    def test_list_authenticated_superuser(self):
        self.users[0].is_superuser = True
        self.users[0].save()

        self.client.force_authenticate(self.users[0])

        response = self.client.get(reverse('ticket-list'))

        self.assertEqual(response.status_code, 200)
        self.assertIn(self.tickets[0].background, response.content)

        body = json.loads(response.content)

        self.assertEqual(body['meta']['total']['all'], 3)

    def test_list_authenticated_with_includes(self):
        self.client.force_authenticate(self.users[0])

        response = self.client.get(
            reverse('ticket-list'), {'include': 'requester,responders.user'})

        self.assertEqual(response.status_code, 200)
        self.assertIn('included', response.content)
        self.assertNotIn(self.responders[0].user.email, response.content)
        self.assertNotIn(self.responders[1].user.email, response.content)

    def test_list_filter_authenticated_by_responders(self):
        self.client.force_authenticate(self.users[0])

        response = self.client.get(
            reverse('ticket-list'), {
                'filter[users]': 'none'
            }
        )

        self.assertEqual(response.status_code, 200)

    def test_get_authenticated(self):
        self.client.force_authenticate(self.users[0])

        response = self.client.get(
            reverse('ticket-detail', args=[self.tickets[0].id]))

        self.assertEqual(response.status_code, 200)
        self.assertIn(self.tickets[0].background, response.content)

    def test_update_authenticated(self):
        ticket = self.tickets[0]
        self.client.force_authenticate(self.users[3])

        new_data = self.as_jsonapi_payload(
            TicketSerializer, ticket, {'background': 'new-background'})

        response = self.client.put(
            reverse('ticket-detail', args=[ticket.id]),
            data=json.dumps(new_data),
            content_type=self.JSON_API_CONTENT_TYPE
        )

        self.assertEqual(response.status_code, 404)

    def test_update_authenticated_author(self):
        ticket = self.tickets[0]
        self.client.force_authenticate(self.tickets[0].requester)

        new_data = self.as_jsonapi_payload(
            TicketSerializer, ticket, {'status': 'closed'})

        response = self.client.put(
            reverse('ticket-detail', args=[ticket.id]),
            data=json.dumps(new_data),
            content_type=self.JSON_API_CONTENT_TYPE
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            Ticket.objects.get(id=self.tickets[0].id).status, 'closed')

    def test_update_authenticated_responder(self):
        ticket = self.tickets[0]
        self.client.force_authenticate(self.users[2])

        new_data = self.as_jsonapi_payload(
            TicketSerializer, ticket, {'status': 'closed'})

        response = self.client.put(
            reverse('ticket-detail', args=[ticket.id]),
            data=json.dumps(new_data),
            content_type=self.JSON_API_CONTENT_TYPE
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            Ticket.objects.get(id=self.tickets[0].id).status, 'closed')

    def test_update_authenticated_superuser(self):
        ticket = self.tickets[0]
        user = self.users[0]
        user.is_superuser = True
        self.client.force_authenticate(user)

        new_data = self.as_jsonapi_payload(
            TicketSerializer, ticket, {'background': 'new-background'})

        response = self.client.put(
            reverse('ticket-detail', args=[ticket.id]),
            data=json.dumps(new_data),
            content_type=self.JSON_API_CONTENT_TYPE
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn('new-background', response.content)

    def test_update_authenticated_superuser_reopen_reason(self):
        ticket = self.tickets[0]
        user = self.users[0]
        user.is_superuser = True
        self.client.force_authenticate(user)

        the_reason = 'The reason...'

        new_data = self.as_jsonapi_payload(
            TicketSerializer, ticket, {
                'status': 'in-progress',
                'reopen_reason': the_reason
            })

        response = self.client.patch(
            reverse('ticket-detail', args=[ticket.id]),
            data=json.dumps(new_data),
            content_type=self.JSON_API_CONTENT_TYPE
        )

        self.assertEqual(response.status_code, 200)

        ticket = Ticket.objects.get(id=ticket.id)
        comment = ticket.comments.first()
        action = Action.objects.filter(target_object_id=str(ticket.id)).first()

        self.assertEqual(ticket.status, 'in-progress')
        self.assertEqual(ticket.comments.count(), 1)
        self.assertEqual(comment.body, the_reason)
        self.assertEqual(action.verb, 'ticket:update:reopen')
        self.assertEqual(action.action, comment)

    def test_update_authenticated_closing_with_deadline_passed(self):
        ticket = self.tickets[0]
        user = self.users[1]
        self.client.force_authenticate(user)

        new_data = self.as_jsonapi_payload(
            TicketSerializer, ticket, {
                'deadline_at': '1900-01-01T00:00',
                'status': Ticket.STATUSES[3][0]
            })

        response = self.client.patch(
            reverse('ticket-detail', args=[ticket.id]),
            data=json.dumps(new_data),
            content_type=self.JSON_API_CONTENT_TYPE
        )

        self.assertEqual(response.status_code, 200)

        reloaded_ticket = Ticket.objects.get(id=ticket.id)

        self.assertEqual(reloaded_ticket.status, 'closed')
        self.assertEqual(
            reloaded_ticket.deadline_at.isoformat(),
            '1900-01-01T00:00:00'
        )

    def test_update_authenticated_deadline_passed(self):
        ticket = self.tickets[0]
        user = self.users[1]
        self.client.force_authenticate(user)

        new_data = self.as_jsonapi_payload(
            TicketSerializer, ticket, {
                'deadline_at': '1900-01-01T00:00',
            })

        response = self.client.patch(
            reverse('ticket-detail', args=[ticket.id]),
            data=json.dumps(new_data),
            content_type=self.JSON_API_CONTENT_TYPE
        )

        self.assertEqual(response.status_code, 422)

        reloaded_ticket = Ticket.objects.get(id=ticket.id)

        self.assertEqual(reloaded_ticket.deadline_at, ticket.deadline_at)

        response = json.loads(response.content)
        self.assertEqual(
            response['errors'][0]['detail']['data/attributes/deadline_at'],
            'The date can not be in the past.'
        )

    def test_update_authenticated_responder_pending_reason(self):
        ticket = self.tickets[0]
        user = self.users[1]
        self.client.force_authenticate(user)

        the_reason = 'The reason...'

        new_data = self.as_jsonapi_payload(
            TicketSerializer, ticket, {
                'status': 'pending',
                'pending_reason': the_reason
            })

        response = self.client.patch(
            reverse('ticket-detail', args=[ticket.id]),
            data=json.dumps(new_data),
            content_type=self.JSON_API_CONTENT_TYPE
        )

        self.assertEqual(response.status_code, 200)

        ticket = Ticket.objects.get(id=ticket.id)
        comment = ticket.comments.first()
        action = Action.objects.filter(target_object_id=str(ticket.id)).first()

        self.assertEqual(ticket.status, 'pending')
        self.assertEqual(ticket.comments.count(), 1)
        self.assertEqual(comment.body, the_reason)
        self.assertEqual(action.verb, 'ticket:update:pending')
        self.assertEqual(action.action, comment)

    def test_create_authenticated(self):
        ticket = self.tickets[0]
        tickets_count = Ticket.objects.count()
        self.client.force_authenticate(self.users[0])

        new_data = self.as_jsonapi_payload(
            TicketSerializer, ticket, {'background': 'ticket-background'})

        response = self.client.post(
            reverse('ticket-list'),
            data=json.dumps(new_data),
            content_type=self.JSON_API_CONTENT_TYPE
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(Ticket.objects.count(), tickets_count + 1)
