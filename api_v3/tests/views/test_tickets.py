import json
import random

from django.conf import settings
from django.template.loader import render_to_string

from api_v3.models import Ticket, Action
from api_v3.factories import (
    ProfileFactory,
    ResponderFactory,
    TicketFactory
)
from .support import ApiTestCase, APIClient, reverse
from api_v3.serializers import TicketSerializer
from api_v3.views.tickets import TicketsEndpoint


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

        self.assertEqual(response.status_code, 401)

    def test_list_authenticated(self):
        self.client.force_authenticate(self.users[0])

        response = self.client.get(reverse('ticket-list'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.tickets[0].background)

        body = json.loads(response.content)

        self.assertEqual(body['meta']['total']['all'], 2)

    def test_list_authenticated_superuser(self):
        self.users[0].is_superuser = True
        self.users[0].save()

        self.client.force_authenticate(self.users[0])

        response = self.client.get(reverse('ticket-list'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.tickets[0].background)

        body = json.loads(response.content)

        self.assertEqual(body['meta']['total']['all'], 3)

    def test_list_authenticated_with_includes(self):
        self.client.force_authenticate(self.users[0])

        response = self.client.get(
            reverse('ticket-list'), {'include': 'requester,responders.user'})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'included')
        self.assertNotContains(response, self.responders[0].user.email)
        self.assertNotContains(response, self.responders[1].user.email)

    def test_list_filter_authenticated_by_requester(self):
        user = self.users[1]
        user.is_superuser = True
        self.client.force_authenticate(user)

        response = self.client.get(
            reverse('ticket-list'), {
                'filter[requester]': self.users[2].id
            }
        )

        self.assertEqual(response.status_code, 200)

        body = json.loads(response.content)
        self.assertEqual(
            body['meta']['filters']['requester'],
            {
                'first-name': self.users[2].first_name,
                'last-name': self.users[2].last_name,
                'email': self.users[2].email
            }
        )

    def test_list_filter_superuser_by_requester(self):
        self.client.force_authenticate(self.users[0])

        response = self.client.get(
            reverse('ticket-list'), {
                'filter[requester]': 'none'
            }
        )

        self.assertEqual(response.status_code, 200)

        body = json.loads(response.content)
        self.assertEqual(body['meta']['filters'], {})

    def test_get_authenticated(self):
        self.client.force_authenticate(self.users[0])

        response = self.client.get(
            reverse('ticket-detail', args=[self.tickets[0].id]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.tickets[0].background)

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
        self.assertContains(response, 'new-background')

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

    def test_update_authenticated_any_status_with_deadline_passed(self):
        ticket = self.tickets[0]
        user = self.users[1]
        self.client.force_authenticate(user)

        statuses = map(lambda s: s[0], Ticket.STATUSES)
        statuses.remove(ticket.status)
        new_status = random.choice(statuses)

        new_data = self.as_jsonapi_payload(
            TicketSerializer, ticket, {
                'deadline_at': '1900-01-01T00:00',
                'status': new_status
            })

        response = self.client.patch(
            reverse('ticket-detail', args=[ticket.id]),
            data=json.dumps(new_data),
            content_type=self.JSON_API_CONTENT_TYPE
        )

        self.assertEqual(response.status_code, 200)

        reloaded_ticket = Ticket.objects.get(id=ticket.id)

        self.assertEqual(reloaded_ticket.status, new_status)
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

    def test_email_notify_when_ticket_created(self):
        self.users[0].is_superuser = True
        self.users[0].save()

        controller = TicketsEndpoint()
        count, emails = controller.email_notify(self.tickets[0])

        self.assertEqual(count, 1)

        self.assertEqual(emails[0], [
            controller.EMAIL_SUBJECT.format(self.tickets[0].id),
            render_to_string(
                'mail/ticket_created.txt',
                dict(
                    ticket=self.tickets[0],
                    name=self.users[0].display_name,
                    site_name=settings.SITE_NAME
                )
            ),
            settings.DEFAULT_FROM_EMAIL,
            [self.users[0].email]
        ])

    def test_email_notify(self):
        controller = TicketsEndpoint()
        count, emails = controller.email_notify(
            self.tickets[0], template='mail/ticket_reopened.txt')

        self.assertEqual(count, 2)

        self.assertEqual(emails[0], [
            controller.EMAIL_SUBJECT.format(self.tickets[0].id),
            render_to_string(
                'mail/ticket_reopened.txt',
                dict(
                    ticket=self.tickets[0],
                    name=self.users[2].display_name,
                    site_name=settings.SITE_NAME
                )
            ),
            settings.DEFAULT_FROM_EMAIL,
            [self.users[2].email]
        ])
        self.assertEqual(emails[1], [
            controller.EMAIL_SUBJECT.format(self.tickets[0].id),
            render_to_string(
                'mail/ticket_reopened.txt',
                dict(
                    ticket=self.tickets[0],
                    name=self.users[1].display_name,
                    site_name=settings.SITE_NAME
                )
            ),
            settings.DEFAULT_FROM_EMAIL,
            [self.users[1].email]
        ])
