import json
from datetime import datetime

from django.conf import settings
from django.template.loader import render_to_string

from api_v3.factories import (
    CommentFactory,
    ProfileFactory,
    ResponderFactory,
    SubscriberFactory,
    TicketFactory
)
from api_v3.models import Action, Ticket, Comment
from api_v3.serializers import CommentSerializer
from api_v3.views.comments import CommentsEndpoint
from .support import ApiTestCase, APIClient, reverse, mail, queue


class CommentsEndpointTestCase(ApiTestCase):

    def setUp(self):
        self.client = APIClient()
        self.users = [
            ProfileFactory.create(email='email1'),
            ProfileFactory.create(),
            ProfileFactory.create(email='email3'),
            ProfileFactory.create(),
            ProfileFactory.create(email='email4')
        ]
        self.tickets = [
            TicketFactory.create(requester=self.users[0])
        ]
        self.responders = [
            ResponderFactory.create(
                ticket=self.tickets[0], user=self.users[2])
        ]
        self.subscribed_email = 'subscribed_email'
        self.subscribers = [
            SubscriberFactory.create(
                ticket=self.tickets[0], user=self.users[4]),
            SubscriberFactory.create(
                ticket=self.tickets[0], email=self.subscribed_email)
        ]
        self.comments = [
            CommentFactory.create(user=self.users[3], ticket=self.tickets[0])
        ]

    def test_list_anonymous(self):
        response = self.client.get(reverse('comment-list'))

        self.assertEqual(response.status_code, 401)

    def test_list_authenticated(self):
        self.client.force_authenticate(self.users[0])

        response = self.client.get(reverse('comment-list'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            json.loads(response.content)['data'][0]['id'],
            str(self.comments[0].id)
        )

    def test_detail_authenticated(self):
        self.client.force_authenticate(self.users[0])

        response = self.client.get(
            reverse('comment-detail', args=[self.comments[0].id]))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            json.loads(response.content)['data']['id'],
            str(self.comments[0].id)
        )

    def test_detail_authenticated_without_access(self):
        self.client.force_authenticate(self.users[1])

        response = self.client.get(
            reverse('comment-detail', args=[self.comments[0].id]))

        self.assertEqual(response.status_code, 404)

    def test_create_authenticated(self):
        self.client.force_authenticate(self.users[0])

        ticket = self.comments[0].ticket
        Ticket.objects.filter(pk=ticket.id).update(updated_at=datetime.min)
        ticket.refresh_from_db()
        old_ticket_updated_at = ticket.updated_at

        comments_count = Comment.objects.count()
        actions_count = Action.objects.filter(
            target_object_id=ticket.id).count()

        new_data = self.as_jsonapi_payload(
            CommentSerializer, self.comments[0], {'body': 'new comment'})

        response = self.client.post(
            reverse('comment-list'),
            data=json.dumps(new_data),
            content_type=self.JSON_API_CONTENT_TYPE
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(Comment.objects.count(), comments_count + 1)
        self.assertEqual(
            Action.objects.filter(
                target_object_id=ticket.id,
                verb='comment:create'
            ).count(),
            actions_count + 1
        )

        ticket.refresh_from_db()

        self.assertGreater(ticket.updated_at, old_ticket_updated_at)

    def test_create_authenticated_without_access(self):
        self.client.force_authenticate(self.users[1])

        comments_count = Comment.objects.count()

        new_data = self.as_jsonapi_payload(
            CommentSerializer, self.comments[0], {'body': 'new comment'})

        response = self.client.post(
            reverse('comment-list'),
            data=json.dumps(new_data),
            content_type=self.JSON_API_CONTENT_TYPE
        )

        self.assertEqual(response.status_code, 422)
        self.assertEqual(Comment.objects.count(), comments_count)

    def test_email_notify(self):
        CommentsEndpoint.email_notify(self.comments[0].id, 'host.tld')
        queue.work(burst=True)

        emails = mail.outbox
        self.assertEqual(len(emails), 5)

        requester_email = [e for e in emails if e.to[0] == self.users[0].email]
        sub_email = [e for e in emails if e.to[0] == self.subscribed_email]
        sub1 = [e for e in emails if e.to[0] == self.subscribers[0].user.email]
        res1 = [e for e in emails if e.to[0] == self.responders[0].user.email]

        self.assertEqual(requester_email[0].to[0], 'email1')
        self.assertEqual(
            requester_email[0].subject,
            CommentsEndpoint.EMAIL_SUBJECT.format(self.tickets[0].id))
        self.assertEqual(
            requester_email[0].from_email, settings.DEFAULT_FROM_EMAIL)
        self.assertEqual(
            requester_email[0].body,
            render_to_string(
                'mail/ticket_comment.txt',
                dict(
                    comment=self.comments[0],
                    name=self.users[0].display_name,
                    request_host='host.tld',
                    site_name=settings.SITE_NAME
                )
            )
        )

        self.assertEqual(sub_email[0].to[0], self.subscribed_email)
        self.assertEqual(
            sub_email[0].body,
            render_to_string(
                'mail/ticket_comment.txt',
                dict(
                    comment=self.comments[0],
                    name=' ',
                    request_host='host.tld',
                    site_name=settings.SITE_NAME
                )
            )
        )

        self.assertEqual(sub1[0].to[0], self.subscribers[0].user.email)
        self.assertEqual(
            sub1[0].body,
            render_to_string(
                'mail/ticket_comment.txt',
                dict(
                    comment=self.comments[0],
                    name=self.subscribers[0].user.display_name,
                    request_host='host.tld',
                    site_name=settings.SITE_NAME
                )
            )
        )

        self.assertEqual(res1[0].to[0], 'email3')
        self.assertEqual(
            res1[0].body,
            render_to_string(
                'mail/ticket_comment.txt',
                dict(
                    comment=self.comments[0],
                    name=self.users[2].display_name,
                    request_host='host.tld',
                    site_name=settings.SITE_NAME
                )
            )
        )
