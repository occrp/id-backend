import json
from datetime import datetime, timedelta

from api_v3.factories import ProfileFactory, ResponderFactory, TicketFactory
from .support import ApiTestCase, APIClient, reverse


class TicketStatsEndpointTestCase(ApiTestCase):

    def setUp(self):
        self.client = APIClient()
        self.users = [
            ProfileFactory.create(),
            ProfileFactory.create(is_staff=True),
            ProfileFactory.create(is_staff=True),
        ]

        self.tickets = [
            TicketFactory.create(
                requester=self.users[0],
                status='cancelled',
                deadline_at=(datetime.utcnow() - timedelta(days=3))
            ),
            TicketFactory.create(
                requester=self.users[0], deadline_at=None, status='new'),
            TicketFactory.create(
                requester=self.users[0], deadline_at=None, status='new'),
            TicketFactory.create(
                requester=self.users[0], deadline_at=None, status='new'),
            TicketFactory.create(
                requester=self.users[0], deadline_at=None, status='new'),
        ]

        self.tickets[0].created_at = datetime.utcnow() - timedelta(days=5)
        self.tickets[0].save()

        self.responders = [
            ResponderFactory.create(
                ticket=self.tickets[0], user=self.users[1]),
            ResponderFactory.create(
                ticket=self.tickets[1], user=self.users[1]),
            ResponderFactory.create(
                ticket=self.tickets[1], user=self.users[2])
        ]

    def test_list_anonymous(self):
        response = self.client.get(reverse('ticket_stats-list'))

        self.assertEqual(response.status_code, 401)

    def test_list_user(self):
        self.client.force_authenticate(self.users[0])

        response = self.client.get(reverse('ticket_stats-list'))

        self.assertEqual(response.status_code, 200)

        body = json.loads(response.content)

        self.assertEqual(len(body['data']), 0)

    def test_list_superuser(self):
        self.users[0].is_superuser = True
        self.users[0].save()
        self.client.force_authenticate(self.users[0])

        response = self.client.get(reverse('ticket_stats-list'))

        self.assertEqual(response.status_code, 200)

        body = json.loads(response.content)

        self.assertEqual(len(body['meta']['total']), 6)

        self.assertEqual(body['meta']['total']['open'], 4)
        self.assertEqual(body['meta']['total']['resolved'], 1)

        self.assertEqual(
            sorted(body['meta']['staff-profile-ids']),
            sorted([self.users[1].id, self.users[2].id])
        )
        self.assertEqual(
            body['meta']['countries'],
            sorted(set([t.country for t in self.tickets]))
        )
        self.assertEqual(len(body['data']), 2)

        new_data = [
            b for b in body['data'] if b['attributes']['status'] == 'new'
        ][0]
        cancelled_data = [
            b for b in body['data'] if b['attributes']['status'] == 'cancelled'
        ][0]

        self.assertEqual(cancelled_data['attributes']['count'], 1)
        self.assertEqual(cancelled_data['attributes']['status'], 'cancelled')
        self.assertEqual(cancelled_data['attributes']['avg-time'], 0)
        self.assertEqual(cancelled_data['attributes']['past-deadline'], 1)
        self.assertEqual(
            cancelled_data['attributes']['date'][:19],
            self.tickets[0].updated_at.replace(
                day=1, hour=0, minute=0, second=0, microsecond=0).isoformat()
        )

        self.assertEqual(new_data['attributes']['count'], 4)
        self.assertEqual(new_data['attributes']['status'], 'new')
        self.assertEqual(new_data['attributes']['avg-time'], 0)
        self.assertEqual(new_data['attributes']['past-deadline'], 0)
        self.assertEqual(
            new_data['attributes']['date'][:19],
            self.tickets[1].created_at.replace(
                day=1, hour=0, minute=0, second=0, microsecond=0).isoformat()
        )

    def test_list_superuser_filter_by_start_end_dates(self):
        self.users[0].is_superuser = True
        self.users[0].save()
        self.client.force_authenticate(self.users[0])

        response = self.client.get(
            reverse('ticket_stats-list') +
            '?filter[created_at__lte]=3000-01-01T00:00:00'
        )

        self.assertEqual(response.status_code, 200)

        body = json.loads(response.content)

        three_months_ago = (
            datetime.utcnow().replace(day=1) - timedelta(days=28 * 3))

        self.assertEqual(body['meta']['end-date'], '3000-01-01T00:00:00')
        self.assertEqual(
            body['meta']['start-date'],
            three_months_ago.replace(
                day=1, hour=0, minute=0, second=0, microsecond=0
            ).isoformat()
        )

    def test_list_superuser_filter_by_responder(self):
        self.users[0].is_superuser = True
        self.users[0].save()
        self.client.force_authenticate(self.users[0])

        response = self.client.get(
            reverse('ticket_stats-list') +
            '?filter[responders__user]={}'.format(self.users[1].id)
        )

        self.assertEqual(response.status_code, 200)

        body = json.loads(response.content)

        self.assertEqual(len(body['meta']['total']), 6)

        self.assertEqual(body['meta']['total']['open'], 1)
        self.assertEqual(body['meta']['total']['avg-time-open'], 0.0)
        self.assertEqual(body['meta']['total']['resolved'], 1)
        self.assertEqual(body['meta']['total']['avg-time-resolved'], 0.0)

        self.assertEqual(body['meta']['staff-profile-ids'], [])
        self.assertEqual(body['meta']['countries'], [])

        self.assertEqual(len(body['data']), 2)

        new_data = [
            b for b in body['data'] if b['attributes']['status'] == 'new'
        ][0]
        cancelled_data = [
            b for b in body['data'] if b['attributes']['status'] == 'cancelled'
        ][0]

        self.assertEqual(cancelled_data['attributes']['count'], 1)
        self.assertEqual(cancelled_data['attributes']['status'], 'cancelled')
        self.assertEqual(cancelled_data['attributes']['avg-time'], 0)
        self.assertEqual(cancelled_data['attributes']['past-deadline'], 1)
        self.assertEqual(
            cancelled_data['attributes']['date'][:19],
            self.tickets[0].updated_at.replace(
                day=1, hour=0, minute=0, second=0, microsecond=0).isoformat()
        )

        self.assertEqual(new_data['attributes']['count'], 1)
        self.assertEqual(new_data['attributes']['status'], 'new')
        self.assertEqual(new_data['attributes']['avg-time'], 0)
        self.assertEqual(new_data['attributes']['past-deadline'], 0)
        self.assertEqual(
            new_data['attributes']['date'][:19],
            datetime.utcnow().replace(
                day=1, hour=0, minute=0, second=0, microsecond=0).isoformat()
        )
