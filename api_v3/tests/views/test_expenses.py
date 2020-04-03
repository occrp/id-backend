import json
from datetime import datetime

from api_v3.factories import (
    ExpenseFactory,
    ProfileFactory,
    TicketFactory
)
from api_v3.models import Action, Expense
from api_v3.serializers import ExpenseSerializer
from .support import ApiTestCase, APIClient, reverse


class ExpensesEndpointTestCase(ApiTestCase):

    def setUp(self):
        self.client = APIClient()
        self.users = [
            ProfileFactory.create(),
            ProfileFactory.create(is_superuser=True),
            ProfileFactory.create()
        ]
        self.tickets = [
            TicketFactory.create(requester=self.users[0])
        ]
        self.expenses = [
            ExpenseFactory.create(user=self.users[2], ticket=self.tickets[0])
        ]

    def test_list_anonymous(self):
        response = self.client.get(reverse('expense-list'))

        self.assertEqual(response.status_code, 401)

    def test_list_authenticated(self):
        self.client.force_authenticate(self.users[0])

        response = self.client.get(reverse('expense-list'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            json.loads(response.content)['data'],
            []
        )

    def test_list_authenticated_superuser(self):
        self.client.force_authenticate(self.users[1])

        response = self.client.get(reverse('expense-list'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            json.loads(response.content)['data'][0]['id'],
            str(self.expenses[0].id)
        )

    def test_detail_authenticated(self):
        self.client.force_authenticate(self.users[0])

        response = self.client.get(
            reverse('expense-detail', args=[self.expenses[0].id]))

        self.assertEqual(response.status_code, 404)

    def test_detail_authenticated_superuser(self):
        self.client.force_authenticate(self.users[1])

        response = self.client.get(
            reverse('expense-detail', args=[self.expenses[0].id]))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            json.loads(response.content)['data']['id'],
            str(self.expenses[0].id)
        )

    def test_create_authenticated(self):
        self.client.force_authenticate(self.users[0])

        expenses_count = Expense.objects.count()

        new_data = self.as_jsonapi_payload(
            ExpenseSerializer,
            ExpenseFactory.build(ticket=self.tickets[0]),
            {'notes': 'new note'}
        )

        response = self.client.post(
            reverse('expense-list'),
            data=json.dumps(new_data),
            content_type=self.JSON_API_CONTENT_TYPE
        )

        self.assertEqual(response.status_code, 422)
        self.assertEqual(Expense.objects.count(), expenses_count)

    def test_create_authenticated_superuser(self):
        self.client.force_authenticate(self.users[1])

        ticket = self.expenses[0].ticket

        expenses_count = Expense.objects.count()
        actions_count = Action.objects.filter(
            target_object_id=ticket.id).count()

        new_data = self.as_jsonapi_payload(
            ExpenseSerializer,
            ExpenseFactory.build(ticket=ticket),
            {'notes': 'new notes'}
        )

        response = self.client.post(
            reverse('expense-list'),
            data=json.dumps(new_data),
            content_type=self.JSON_API_CONTENT_TYPE
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(Expense.objects.count(), expenses_count + 1)
        self.assertEqual(
            Action.objects.filter(
                target_object_id=ticket.id,
                verb='expense:create'
            ).count(),
            actions_count + 1
        )

    def test_update_authenticated(self):
        self.client.force_authenticate(self.users[0])

        new_data = self.as_jsonapi_payload(
            ExpenseSerializer, self.expenses[0], {'notes': 'update note'}
        )

        response = self.client.put(
            reverse('expense-detail', args=[self.expenses[0].id]),
            data=json.dumps(new_data),
            content_type=self.JSON_API_CONTENT_TYPE
        )

        self.assertEqual(response.status_code, 404)

    def test_update_authenticated_superuser(self):
        self.client.force_authenticate(self.users[1])

        self.expenses[0].ticket

        expenses_count = Expense.objects.count()

        new_date = datetime.utcnow()
        new_data = self.as_jsonapi_payload(
            ExpenseSerializer,
            self.expenses[0],
            {'notes': 'update notes', 'created_at': new_date.isoformat()}
        )

        response = self.client.put(
            reverse('expense-detail', args=[self.expenses[0].id]),
            data=json.dumps(new_data),
            content_type=self.JSON_API_CONTENT_TYPE
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Expense.objects.count(), expenses_count)

        expense = Expense.objects.get(id=self.expenses[0].id)
        self.assertEqual(expense.notes, 'update notes')
        self.assertEqual(expense.created_at, new_date)

    def test_delete_authenticated(self):
        self.client.force_authenticate(self.users[0])

        response = self.client.delete(
            reverse('expense-detail', args=[self.expenses[0].id])
        )

        self.assertEqual(response.status_code, 404)

    def test_delete_authenticated_superuser(self):
        self.client.force_authenticate(self.users[1])

        actions_count = Action.objects.filter(
            target_object_id=self.expenses[0].ticket.id).count()

        response = self.client.delete(
            reverse('expense-detail', args=[self.expenses[0].id])
        )

        self.assertEqual(response.status_code, 204)
        self.assertEqual(
            Expense.objects.filter(id=self.expenses[0].id).count(), 0
        )
        self.assertEqual(
            Action.objects.filter(
                target_object_id=self.tickets[0].id,
                verb='expense:destroy'
            ).count(),
            actions_count + 1
        )
