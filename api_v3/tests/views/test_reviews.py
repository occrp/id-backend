import json

from django.conf import settings

from api_v3.factories import (
    ProfileFactory,
    ReviewFactory,
    TicketFactory
)
from api_v3.models import Action, Review, Ticket
from api_v3.serializers import ReviewSerializer
from api_v3.views.reviews import ReviewsEndpoint
from .support import ApiTestCase, APIClient, reverse, mail, queue


class ReviewesEndpointTestCase(ApiTestCase):

    def setUp(self):
        self.client = APIClient()
        self.users = [
            ProfileFactory.create(email='email1')
        ]
        self.tickets = [
            TicketFactory.create(
                requester=self.users[0],
                status=Ticket.STATUSES[3][0]
            )
        ]

    def test_list_anonymous(self):
        response = self.client.get(reverse('review-list'))

        self.assertEqual(response.status_code, 405)

    def test_create_anonymous_no_token(self):
        review = ReviewFactory.build()
        new_data = self.as_jsonapi_payload(ReviewSerializer, review)

        response = self.client.post(
            reverse('review-list'),
            data=json.dumps(new_data),
            content_type=self.JSON_API_CONTENT_TYPE
        )

        self.assertEqual(response.status_code, 422)

    def test_create_anonymous(self):
        review = ReviewFactory.build()
        token = Review.ticket_to_token(self.tickets[0])
        new_data = self.as_jsonapi_payload(
            ReviewSerializer, review, {'token': token})

        reviews_count = Review.objects.count()
        actions_count = Action.objects.filter(
            target_object_id=self.tickets[0].id).count()

        response = self.client.post(
            reverse('review-list'),
            data=json.dumps(new_data),
            content_type=self.JSON_API_CONTENT_TYPE
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(Review.objects.count(), reviews_count + 1)
        self.assertEqual(
            Action.objects.filter(
                target_object_id=self.tickets[0].id,
                verb='review:create'
            ).count(),
            actions_count + 1
        )

    def test_email_notify(self):
        ReviewsEndpoint.email_notify(
            self.tickets[0].id, 'host.tld', _schedule_at='0d')
        queue.work(burst=True)

        emails = mail.outbox
        self.assertEqual(len(emails), 1)

        requester_email = [e for e in emails if e.to[0] == self.users[0].email]

        self.assertEqual(requester_email[0].to[0], 'email1')
        self.assertEqual(
            requester_email[0].subject,
            ReviewsEndpoint.EMAIL_SUBJECT.format(self.tickets[0].id))
        self.assertEqual(
            requester_email[0].from_email, settings.DEFAULT_FROM_EMAIL)
        self.assertIn(
            '{request_host}/tickets/{ticket.id}/review?token='.format(
                request_host='host.tld',
                ticket=self.tickets[0]
            ),
            requester_email[0].body
        )
