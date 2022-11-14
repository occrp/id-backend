import json

from api_v3.models import Review
from api_v3.factories import ProfileFactory, ResponderFactory, ReviewFactory
from .support import ApiTestCase, APIClient, reverse


class ReviewStatsEndpointTestCase(ApiTestCase):

    def setUp(self):
        self.client = APIClient()
        self.users = [
            ProfileFactory.create(),
            ProfileFactory.create(is_staff=True)
        ]

        review = ReviewFactory.create(
            ticket__requester=self.users[0],
            rating=Review.RATINGS[2][0]
        )

        self.reviews = [
            review,
            ReviewFactory.create(
                ticket__requester=self.users[0],
                ticket=review.ticket,
                rating=Review.RATINGS[2][0]
            ),
            ReviewFactory.create(
                ticket__requester=self.users[0],
                rating=Review.RATINGS[2][0]
            )
        ]

    def test_list_anonymous(self):
        response = self.client.get(reverse('review_stats-list'))

        self.assertEqual(response.status_code, 401)

    def test_list_user(self):
        self.client.force_authenticate(self.users[0])

        response = self.client.get(reverse('review_stats-list'))

        self.assertEqual(response.status_code, 403)

    def test_list_superuser(self):
        self.users[1].is_staff = False
        self.users[1].is_superuser = True
        self.users[1].save()
        self.client.force_authenticate(self.users[1])

        response = self.client.get(reverse('review_stats-list'))

        self.assertEqual(response.status_code, 403)

    def test_list_staff(self):
        self.client.force_authenticate(self.users[1])

        response = self.client.get(reverse('review_stats-list'))

        self.assertEqual(response.status_code, 200)

        body = json.loads(response.content)

        self.assertEqual(len(body['data']), 2)

        if (
            body['data'][0]['relationships']['ticket']['data']['id'] ==
            self.reviews[0].ticket.id
        ):
            ticket_1_data = body['data'][0]
            ticket_2_data = body['data'][1]
        else:
            ticket_2_data = body['data'][0]
            ticket_1_data = body['data'][1]

        self.assertEqual(ticket_1_data['attributes']['ratings'], 2)
        self.assertEqual(ticket_1_data['attributes']['count'], 2)
        self.assertEqual(ticket_2_data['attributes']['ratings'], 1)
        self.assertEqual(ticket_2_data['attributes']['count'], 1)

    def test_list_staff_filter_by_start_end_dates(self):
        self.client.force_authenticate(self.users[1])

        response = self.client.get(
            reverse('review_stats-list') +
            '?filter[created_at__gte]=3000-01-01T00:00:00'
        )

        self.assertEqual(response.status_code, 200)

        body = json.loads(response.content)

        self.assertEqual(len(body['data']), 0)

    def test_list_staff_group_by_responder(self):
        ResponderFactory.create(
            ticket=self.reviews[0].ticket, user=self.users[1])

        self.client.force_authenticate(self.users[1])

        response = self.client.get(
            reverse('review_stats-list') + '?by=responder'
        )

        self.assertEqual(response.status_code, 200)

        body = json.loads(response.content)

        self.assertEqual(len(body['data']), 2)

        if body['data'][0]['relationships']['responder']['data']:
            responder_data = body['data'][0]
            non_responder_data = body['data'][1]
        else:
            responder_data = body['data'][1]
            non_responder_data = body['data'][0]

        self.assertEqual(responder_data['attributes']['ratings'], 2)
        self.assertEqual(responder_data['attributes']['count'], 2)
        self.assertEqual(non_responder_data['attributes']['ratings'], 1)
        self.assertEqual(non_responder_data['attributes']['count'], 1)
