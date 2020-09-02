# -*- coding: utf-8 -*-
from api_v3.factories import (
    ProfileFactory,
    TicketFactory
)
from .support import TestCase, APIClient, reverse


class TicketExportsEndpointTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.users = [
            ProfileFactory.create(),
            ProfileFactory.create(is_superuser=True, is_staff=True)
        ]
        self.tickets = [
            TicketFactory.create(requester=self.users[0]),
            TicketFactory.create(requester=self.users[0])
        ]

    def test_list_anonymous(self):
        response = self.client.get(reverse('ticket_exports-list'))

        self.assertEqual(response.status_code, 401)

    def test_list_not_staff(self):
        self.client.force_authenticate(self.users[0])
        response = self.client.get(reverse('ticket_exports-list'))

        self.assertEqual(response.status_code, 403)

    def test_list_staff(self):
        self.client.force_authenticate(self.users[1])
        response = self.client.get(reverse('ticket_exports-list'))

        self.assertEqual(response.status_code, 200)
        self.assertIn(
            'filename="tickets-',
            response.get('Content-Disposition')
        )

        csv_data = str(response.getvalue())

        self.assertIn('RequestType,Priority', csv_data)
        self.assertIn(str(self.tickets[0].id), csv_data)
        self.assertIn(str(self.tickets[1].id), csv_data)
