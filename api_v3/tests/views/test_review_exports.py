# -*- coding: utf-8 -*-
from api_v3.factories import ProfileFactory, ReviewFactory
from .support import TestCase, APIClient, reverse


class ExpenseExportsEndpointTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.users = [
            ProfileFactory.create(),
            ProfileFactory.create(is_superuser=True, is_staff=True)
        ]
        self.reviews = [
            ReviewFactory.create(),
            ReviewFactory.create()
        ]

    def test_list_anonymous(self):
        response = self.client.get(reverse('review_exports-list'))

        self.assertEqual(response.status_code, 401)

    def test_list_not_staff(self):
        self.client.force_authenticate(self.users[0])
        response = self.client.get(reverse('review_exports-list'))

        self.assertEqual(response.status_code, 403)

    def test_list_staff(self):
        self.client.force_authenticate(self.users[1])
        response = self.client.get(reverse('review_exports-list'))

        self.assertEqual(response.status_code, 200)
        self.assertIn(
            'filename="reviews-',
            response.get('Content-Disposition')
        )

        csv_data = str(response.getvalue())

        self.assertIn('Ticket,Date,Rating,Link', csv_data)
        self.assertIn(str(self.reviews[0].body), csv_data)
        self.assertIn(str(self.reviews[0].ticket.id), csv_data)
        self.assertIn(str(self.reviews[1].body), csv_data)
        self.assertIn(str(self.reviews[1].ticket.id), csv_data)
