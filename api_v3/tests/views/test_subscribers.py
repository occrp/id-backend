import json

from django.conf import settings
from django.template.loader import render_to_string

from api_v3.factories import (
    ProfileFactory, TicketFactory, ResponderFactory, SubscriberFactory)
from api_v3.factories.support import Faker
from api_v3.models import Subscriber, Action
from api_v3.serializers import SubscriberSerializer
from api_v3.serializers.mixins import ResponderSubscriberSerializer
from api_v3.views.subscribers import SubscribersEndpoint
from .support import ApiTestCase, APIClient, reverse


class SubscribersEndpointTestCase(ApiTestCase):

    def setUp(self):
        self.client = APIClient()
        self.users = [
            ProfileFactory.create(),
            ProfileFactory.create(),
            ProfileFactory.create(is_superuser=True),
            ProfileFactory.create()
        ]
        self.tickets = [
            TicketFactory.create(requester=self.users[0]),
            TicketFactory.create(requester=self.users[1])
        ]
        self.responders = [
            ResponderFactory.create(ticket=self.tickets[0], user=self.users[1]),
            ResponderFactory.create(ticket=self.tickets[1], user=self.users[2])
        ]
        self.subscriber = SubscriberFactory.create(
            ticket=self.tickets[0], user=self.users[0]
        )

    def test_create_arbitrary_user(self):
        self.client.force_authenticate(self.users[3])

        new_data = self.as_jsonapi_payload(
            SubscriberSerializer, self.subscriber)

        new_data['data']['attributes']['email'] = self.users[3].email

        response = self.client.post(
            reverse('subscriber-list'),
            data=json.dumps(new_data),
            content_type=self.JSON_API_CONTENT_TYPE
        )

        self.assertEqual(response.status_code, 422)

        response = json.loads(response.content)
        self.assertEqual(
            response['errors'][0]['detail']['data/attributes/ticket'],
            'Ticket not found.'
        )

    def test_create_superuser_user_is_subscriber(self):
        self.client.force_authenticate(self.users[2])

        new_data = self.as_jsonapi_payload(
            SubscriberSerializer, self.subscriber)

        new_data['data']['attributes']['email'] = self.subscriber.user.email

        response = self.client.post(
            reverse('subscriber-list'),
            data=json.dumps(new_data),
            content_type=self.JSON_API_CONTENT_TYPE
        )

        self.assertEqual(response.status_code, 422)

        response = json.loads(response.content)
        self.assertEqual(
            response['errors'][0]['source']['pointer'],
            '/data/attributes/user'
        )
        self.assertEqual(
            response['errors'][0]['detail'],
            'Subscriber already exists.'
        )

    def test_create_superuser_user_is_responder(self):
        self.client.force_authenticate(self.users[2])

        new_data = self.as_jsonapi_payload(
            SubscriberSerializer, self.subscriber)

        new_data['data']['attributes']['email'] = self.users[1].email

        response = self.client.post(
            reverse('subscriber-list'),
            data=json.dumps(new_data),
            content_type=self.JSON_API_CONTENT_TYPE
        )
        self.assertEqual(response.status_code, 422)

        response = json.loads(response.content)
        self.assertEqual(
            response['errors'][0]['source']['pointer'],
            '/data/attributes/user'
        )
        self.assertEqual(
            response['errors'][0]['detail'],
            'User is a responder.'
        )

    def test_create_superuser(self):
        self.client.force_authenticate(self.users[2])

        subscribers_count = Subscriber.objects.count()

        new_data = self.as_jsonapi_payload(
            SubscriberSerializer, self.subscriber)

        new_data['data']['attributes']['email'] = self.users[2].email

        response = self.client.post(
            reverse('subscriber-list'),
            data=json.dumps(new_data),
            content_type=self.JSON_API_CONTENT_TYPE
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(Subscriber.objects.count(), subscribers_count + 1)

    def test_create_non_superuser(self):
        self.client.force_authenticate(self.users[0])

        subscribers_count = Subscriber.objects.count()

        new_data = self.as_jsonapi_payload(
            SubscriberSerializer, self.subscriber)

        new_data['data']['attributes']['email'] = self.users[3].email

        response = self.client.post(
            reverse('subscriber-list'),
            data=json.dumps(new_data),
            content_type=self.JSON_API_CONTENT_TYPE
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(Subscriber.objects.count(), subscribers_count + 1)

    def test_create_non_superuser_arbitrary_email(self):
        self.client.force_authenticate(self.users[0])

        subscribers_count = Subscriber.objects.count()

        new_data = self.as_jsonapi_payload(
            SubscriberSerializer, self.subscriber)

        new_email = Faker('email').generate({})
        new_data['data']['attributes']['user'] = {}
        new_data['data']['attributes']['email'] = new_email

        response = self.client.post(
            reverse('subscriber-list'),
            data=json.dumps(new_data),
            content_type=self.JSON_API_CONTENT_TYPE
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(Subscriber.objects.count(), subscribers_count + 1)
        self.assertEqual(Subscriber.objects.last().email, new_email)

    def test_create_non_superuser_arbitrary_email_exists(self):
        self.client.force_authenticate(self.users[0])

        new_email = Faker('email').generate({})
        Subscriber.objects.create(
            ticket=self.subscriber.ticket, email=new_email)

        subscribers_count = Subscriber.objects.count()

        new_data = self.as_jsonapi_payload(
            SubscriberSerializer, self.subscriber)
        new_data['data']['attributes'].pop('user')
        new_data['data']['attributes']['email'] = new_email

        response = self.client.post(
            reverse('subscriber-list'),
            data=json.dumps(new_data),
            content_type=self.JSON_API_CONTENT_TYPE
        )

        self.assertEqual(response.status_code, 422)
        self.assertEqual(Subscriber.objects.count(), subscribers_count)

        data = json.loads(response.content)

        self.assertEqual(
            data['errors'][0]['source']['pointer'],
            '/data/attributes/email'
        )
        self.assertEqual(
            data['errors'][0]['detail'],
            ResponderSubscriberSerializer.EMAIL_SUBSCRIBER_ERROR_MESSAGE
        )

    def test_delete_non_superuser(self):
        self.client.force_authenticate(self.users[3])

        response = self.client.delete(
            reverse('subscriber-detail', args=[self.subscriber.id]),
            content_type=self.JSON_API_CONTENT_TYPE
        )

        self.assertEqual(response.status_code, 404)

    def test_delete_self_subscriber(self):
        self.client.force_authenticate(self.users[0])

        subscribers_count = Subscriber.objects.count()

        response = self.client.delete(
            reverse('subscriber-detail', args=[self.subscriber.id]),
            content_type=self.JSON_API_CONTENT_TYPE
        )

        self.assertEqual(response.status_code, 204)
        self.assertEqual(Subscriber.objects.count(), subscribers_count - 1)

    def test_delete_superuser(self):
        self.client.force_authenticate(self.users[2])

        subscribers_count = Subscriber.objects.count()

        response = self.client.delete(
            reverse('subscriber-detail', args=[self.subscriber.id]),
            content_type=self.JSON_API_CONTENT_TYPE
        )

        self.assertEqual(response.status_code, 204)
        self.assertEqual(Subscriber.objects.count(), subscribers_count - 1)

    def test_list_anonymous(self):
        response = self.client.get(reverse('subscriber-list'))

        self.assertEqual(response.status_code, 401)

    def test_list_authenticated(self):
        self.client.force_authenticate(self.users[0])

        response = self.client.get(reverse('subscriber-list'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(json.loads(response.content)['data']), 1)
        self.assertEqual(
            json.loads(response.content)['data'][0]['id'],
            str(self.subscriber.id)
        )

    def test_get_authenticated_subscriber(self):
        self.client.force_authenticate(self.users[0])

        response = self.client.get(
            reverse('subscriber-detail', args=[self.subscriber.id]))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            json.loads(response.content)['data']['id'],
            str(self.subscriber.id)
        )

    def test_get_authenticated_responder(self):
        self.client.force_authenticate(self.users[1])

        response = self.client.get(
            reverse('subscriber-detail', args=[self.subscriber.id]))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            json.loads(response.content)['data']['id'],
            str(self.subscriber.id)
        )

    def test_get_authenticated_without_access(self):
        self.client.force_authenticate(self.users[3])

        response = self.client.get(
            reverse('subscriber-detail', args=[self.subscriber.id]))

        self.assertEqual(response.status_code, 404)

    def test_email_notify(self):
        controller = SubscribersEndpoint()

        activity = Action(
            actor=self.subscriber.user,
            action=self.users[0],
            target=self.subscriber.ticket,
            verb='test-subscriber-added'
        )

        count, emails = controller.email_notify(activity, self.subscriber)

        self.assertEqual(count, 1)

        self.assertEqual(emails[0], [
            controller.EMAIL_SUBJECT.format(self.tickets[0].id),
            render_to_string(
                'mail/subscriber_added.txt', {
                    'ticket': self.tickets[0],
                    'name': self.users[0].display_name,
                    'site_name': settings.SITE_NAME
                }
            ),
            settings.DEFAULT_FROM_EMAIL,
            [self.users[0].email]
        ])
