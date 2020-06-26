# -*- coding: utf-8 -*-
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
from .support import ApiTestCase, APIClient, reverse, mail, queue
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

        status1 = self.tickets[0].status
        status2 = Ticket.STATUSES[1][0]
        cancelled = Ticket.STATUSES[4][0]
        self.tickets[1].status = cancelled
        self.tickets[1].save()

        self.client.force_authenticate(self.users[0])

        response = self.client.get(
            reverse('ticket-list'),
            {'filter[status__in]': ','.join([status1, status2])}
        )

        self.assertEqual(response.status_code, 200)

        body = json.loads(response.content)

        self.assertEqual(body['meta']['total']['all'], 3)
        self.assertNotEqual(body['meta']['total'][cancelled], 0)

        self.assertContains(response, self.tickets[0].background)

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
                'filter[requester]': self.users[0].id
            }
        )

        self.assertEqual(response.status_code, 200)

        body = json.loads(response.content)
        self.assertEqual(body['meta']['total']['all'], 2)
        self.assertEqual(
            body['meta']['filters']['requester'],
            {
                'first-name': self.users[0].first_name,
                'last-name': self.users[0].last_name,
                'email': self.users[0].email
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

    def test_list_search(self):
        self.client.force_authenticate(self.users[0])
        ticket = self.tickets[0]
        keywords = 'Investigative Dashboard Proj€ct'
        ticket.background += keywords
        ticket.save()

        response = self.client.get(
            reverse('ticket-list'), {'filter[search]': keywords}
        )

        self.assertEqual(response.status_code, 200)

        body = json.loads(response.content)
        self.assertEqual(len(body['data']), 1)
        self.assertEqual(body['data'][0]['id'], str(ticket.id))
        self.assertEqual(body['meta']['total']['all'], 1)

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

        statuses = [s[0] for s in Ticket.STATUSES]
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
            TicketSerializer, ticket,
            {'background': 'ticket-background', 'country': 'MD'}
        )

        response = self.client.post(
            reverse('ticket-list'),
            data=json.dumps(new_data),
            content_type=self.JSON_API_CONTENT_TYPE
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(
            Ticket.objects.filter(countries__contains=['MD']).count(), 1)
        self.assertEqual(Ticket.objects.count(), tickets_count + 1)

    def test_email_notify_when_ticket_created(self):
        settings.DEFAULT_NOTIFY_EMAILS.append(self.users[0].email)

        self.users[0].is_superuser = True
        self.users[0].save()

        TicketsEndpoint.email_notify(self.tickets[0].id, 'host.tld')
        queue.work(burst=True)
        emails = mail.outbox
        self.assertEqual(len(emails), 1)

        self.assertEqual(
            emails[0].subject,
            TicketsEndpoint.EMAIL_SUBJECT.format(self.tickets[0].id)
        )
        self.assertEqual(emails[0].from_email, settings.DEFAULT_FROM_EMAIL)
        self.assertEqual(emails[0].to, [self.users[0].email])
        self.assertEqual(
            emails[0].body,
            render_to_string(
                'mail/ticket_created.txt',
                dict(
                    ticket=self.tickets[0],
                    name=self.users[0].display_name,
                    request_host='host.tld',
                    site_name=settings.SITE_NAME
                )
            )
        )

        settings.DEFAULT_NOTIFY_EMAILS.remove(self.users[0].email)

    def test_email_notify(self):
        TicketsEndpoint.email_notify(
            self.tickets[0].id, 'host.tld', template='mail/ticket_reopened.txt')

        queue.work(burst=True)
        emails = mail.outbox
        self.assertEqual(len(emails), 2)

        email = [e for e in emails if e.to[0] == self.users[2].email][0]

        self.assertEqual(
            email.subject,
            TicketsEndpoint.EMAIL_SUBJECT.format(self.tickets[0].id)
        )
        self.assertEqual(email.from_email, settings.DEFAULT_FROM_EMAIL)
        self.assertEqual(
            email.body,
            render_to_string(
                'mail/ticket_reopened.txt',
                dict(
                    ticket=self.tickets[0],
                    name=self.users[2].display_name,
                    request_host='host.tld',
                    site_name=settings.SITE_NAME
                )
            )
        )

        email = [e for e in emails if e.to[0] == self.users[1].email][0]

        self.assertEqual(
            email.subject,
            TicketsEndpoint.EMAIL_SUBJECT.format(self.tickets[0].id)
        )
        self.assertEqual(email.from_email, settings.DEFAULT_FROM_EMAIL)
        self.assertEqual(
            email.body,
            render_to_string(
                'mail/ticket_reopened.txt',
                dict(
                    ticket=self.tickets[0],
                    name=self.users[1].display_name,
                    request_host='host.tld',
                    site_name=settings.SITE_NAME
                )
            )
        )
