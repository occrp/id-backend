# -*- coding: utf-8 -*-
from api_v3.factories import (
    ProfileFactory,
    TicketFactory,
    ExpenseFactory
)
from .support import TestCase, APIClient, reverse


class ExpenseExportsEndpointTestCase(TestCase):
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
        self.expenses = [
            ExpenseFactory.create(user=self.users[0], ticket=self.tickets[0]),
            ExpenseFactory.create(user=self.users[0], ticket=self.tickets[1])
        ]

    def test_list_anonymous(self):
        response = self.client.get(reverse('expense_exports-list'))

        self.assertEqual(response.status_code, 401)

    def test_list_not_staff(self):
        self.client.force_authenticate(self.users[0])
        response = self.client.get(reverse('expense_exports-list'))

        self.assertEqual(response.status_code, 403)

    def test_list_staff(self):
        self.client.force_authenticate(self.users[1])
        response = self.client.get(reverse('expense_exports-list'))

        self.assertEqual(response.status_code, 200)
        self.assertIn(
            'filename="expenses-',
            response.get('Content-Disposition')
        )

        csv_data = str(response.getvalue(), encoding='utf-8', errors='ignore')

        self.assertIn('Currency,Rating', csv_data)
        self.assertIn(str(self.tickets[0].id), csv_data)
        self.assertIn(str(self.expenses[0].scope), csv_data)
        self.assertIn(str(self.tickets[1].id), csv_data)
        self.assertIn(str(self.expenses[1].scope), csv_data)
