import io
import json
from datetime import datetime

from django.conf import settings
from django.test import TestCase
from django.core.urlresolvers import reverse
from rest_framework.test import APIClient
from rest_framework_json_api.utils import(
    get_resource_type_from_serializer, format_keys)

from api_v3.models import(
    Ticket, Profile, Responder, Attachment, Comment, Action)
from api_v3.serializers import(
    ProfileSerializer, TicketSerializer,
    CommentSerializer, ResponderSerializer)


class ApiTestCase(TestCase):

    JSON_API_CONTENT_TYPE = 'application/vnd.api+json'

    def as_jsonapi_payload(self, serializer_class, obj, update={}):
        data = serializer_class(obj).data
        data.update(update)
        return dict(
            data=dict(
                id=obj.id,
                attributes=format_keys(data, settings.JSON_API_FORMAT_KEYS),
                type=get_resource_type_from_serializer(serializer_class)
            )
        )


class SessionsEndpointTestCase(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.users = [
            Profile.objects.create(
                email='email1',
                last_login=datetime.utcnow()
            ),
            Profile.objects.create(
                email='email2',
                last_login=datetime.utcnow()
            )
        ]

    def test_me_anonymous(self):
        response = self.client.get(reverse('me-list'))

        self.assertEqual(response.status_code, 401)

    def test_me_authenticated(self):
        self.client.force_authenticate(self.users[0])

        response = self.client.get(reverse('me-list'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            json.loads(response.content),
            ProfileSerializer(self.users[0]).data
        )


class OpsEndpointTestCase(TestCase):

    def setUp(self):
        self.client = APIClient()

    def test_retrieve_anonymous_wrong_op_name(self):
        op_name = 'wrong-op'
        response = self.client.get(reverse('ops-detail', args=[op_name]))

        self.assertEqual(response.status_code, 200)
        self.assertNotIn(op_name, response.content)

    def test_retrieve_anonymous_good_op_name(self):
        op_name = 'email_ticket_digest'
        response = self.client.get(reverse('ops-detail', args=[op_name]))

        self.assertEqual(response.status_code, 200)
        self.assertIn(op_name, response.content)


class TicketsEndpointTestCase(ApiTestCase):

    def setUp(self):
        self.client = APIClient()
        self.users = [
            Profile.objects.create(
                email='email1',
                last_login=datetime.utcnow()
            ),
            Profile.objects.create(
                email='email2',
                last_login=datetime.utcnow()
            )
        ]

        self.tickets = [
            Ticket.objects.create(background='test1', requester=self.users[0]),
            Ticket.objects.create(background='test2', requester=self.users[1])
        ]

    def test_list_anonymous(self):
        response = self.client.get(reverse('ticket-list'))

        self.assertEqual(response.status_code, 401)

    def test_list_authenticated(self):
        self.client.force_authenticate(self.users[0])

        response = self.client.get(reverse('ticket-list'))

        self.assertEqual(response.status_code, 200)
        self.assertIn(self.tickets[0].background, response.content)

    def test_list_authenticated_with_includes(self):
        self.client.force_authenticate(self.users[0])

        response = self.client.get(
            reverse('ticket-list'), {'include': 'requester'})

        self.assertEqual(response.status_code, 200)
        self.assertIn('included', response.content)

    def test_get_authenticated(self):
        self.client.force_authenticate(self.users[0])

        response = self.client.get(
            reverse('ticket-detail', args=[self.tickets[0].id]))

        self.assertEqual(response.status_code, 200)
        self.assertIn(self.tickets[0].background, response.content)

    def test_update_authenticated(self):
        ticket = self.tickets[0]
        self.client.force_authenticate(self.users[0])

        new_data = self.as_jsonapi_payload(
            TicketSerializer, ticket, {'background': 'new-background'})

        response = self.client.put(
            reverse('ticket-detail', args=[ticket.id]),
            data=json.dumps(new_data),
            content_type=self.JSON_API_CONTENT_TYPE
        )

        self.assertEqual(response.status_code, 404)

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
        self.assertIn('new-background', response.content)

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

        response = self.client.put(
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
        self.assertEqual(action.verb, 'ticket:update:status_in-progress')
        self.assertEqual(action.action, comment)

    def test_create_authenticated(self):
        ticket = self.tickets[0]
        tickets_count = Ticket.objects.count()
        self.client.force_authenticate(self.users[0])

        new_data = self.as_jsonapi_payload(
            TicketSerializer, ticket, {'background': 'ticket-background'})

        response = self.client.post(
            reverse('ticket-list'),
            data=json.dumps(new_data),
            content_type=self.JSON_API_CONTENT_TYPE
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(Ticket.objects.count(), tickets_count + 1)


class ProfilesEndpointTestCase(ApiTestCase):

    def setUp(self):
        self.client = APIClient()
        self.users = [
            Profile.objects.create(
                first_name='First',
                last_name='User',
                email='email1',
                last_login=datetime.utcnow()
            ),
            Profile.objects.create(
                first_name='Second',
                last_name='Profile',
                email='email2',
                last_login=datetime.utcnow()
            )
        ]

    def test_list_anonymous(self):
        response = self.client.get(reverse('profile-list'))

        self.assertEqual(response.status_code, 401)

    def test_list_authenticated_no_staff_or_superuser(self):
        self.client.force_authenticate(self.users[0])

        response = self.client.get(reverse('profile-list'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content)['data'], [])

    def test_list_authenticated(self):
        self.users[0].is_staff = True
        self.users[0].save()
        self.users[1].is_superuser = True
        self.users[1].save()
        self.client.force_authenticate(self.users[0])

        response = self.client.get(reverse('profile-list'))

        self.assertEqual(response.status_code, 200)
        self.assertIn(self.users[0].email, response.content)
        self.assertIn(self.users[1].email, response.content)

    def test_list_filter_authenticated(self):
        self.users[0].is_staff = True
        self.users[0].save()
        self.users[1].is_staff = True
        self.users[1].save()
        self.client.force_authenticate(self.users[0])

        response = self.client.get(
            reverse('profile-list'), {
                'filter[name]': self.users[1].first_name[1:4]
            }
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn(self.users[1].email, response.content)
        self.assertNotIn(self.users[0].email, response.content)

    def test_list_filter_authenticated_by_responders(self):
        self.client.force_authenticate(self.users[0])

        response = self.client.get(
            reverse('profile-list'), {
                'filter[responders]': 'none'
            }
        )

        self.assertEqual(response.status_code, 200)

    def test_update_authenticated_not_owned_profile(self):
        self.users[1].is_staff = True
        self.users[1].save()
        self.client.force_authenticate(self.users[0])

        new_data = self.as_jsonapi_payload(
            ProfileSerializer, self.users[1], {'bio': 'Short Bio'})

        response = self.client.patch(
            reverse('profile-detail', args=[self.users[1].id]),
            data=json.dumps(new_data),
            content_type=ApiTestCase.JSON_API_CONTENT_TYPE
        )

        self.assertEqual(response.status_code, 404)

    def test_update_authenticated(self):
        self.users[0].is_staff = True
        self.users[0].save()
        self.client.force_authenticate(self.users[0])

        email = 'ignored@email.address'
        new_data = self.as_jsonapi_payload(
            ProfileSerializer, self.users[0], {
                'email': email, 'bio': 'Short Bio'})

        response = self.client.patch(
            reverse('profile-detail', args=[self.users[0].id]),
            data=json.dumps(new_data),
            content_type=ApiTestCase.JSON_API_CONTENT_TYPE
        )

        self.assertEqual(response.status_code, 200)
        self.assertNotIn(email, response.content)
        self.assertIn('Short Bio', response.content)


class ActivitiesEndpointTestCase(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.users = [
            Profile.objects.create(
                email='email1',
                last_login=datetime.utcnow()
            ),
            Profile.objects.create(
                email='email2',
                last_login=datetime.utcnow()
            )
        ]
        self.tickets = [
            Ticket.objects.create(background='test1', requester=self.users[1])
        ]
        self.attachments = [
            Attachment.objects.create(
                user=self.users[0],
                ticket=self.tickets[0],
            )
        ]
        self.activities = [
            Action.objects.create(
                actor=self.users[1],
                target=self.tickets[0],
                action=self.attachments[0],
                verb='test-action'
            )
        ]

    def test_list_anonymous(self):
        response = self.client.get(reverse('action-list'))

        self.assertEqual(response.status_code, 401)

    def test_list_authenticated_no_tickets(self):
        self.client.force_authenticate(self.users[0])

        response = self.client.get(reverse('profile-list'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content)['data'], [])

    def test_list_authenticated(self):
        self.client.force_authenticate(self.users[1])

        response = self.client.get(reverse('action-list'))

        self.assertEqual(response.status_code, 200)
        self.assertIn(self.activities[0].verb, response.content)

    def test_list_authenticated_with_includes(self):
        self.client.force_authenticate(self.users[1])

        response = self.client.get(
            reverse('action-list'), {'include': 'attachment'})

        self.assertEqual(response.status_code, 200)
        self.assertIn('included', response.content)


class AttachmentsEndpointTestCase(ApiTestCase):

    def setUp(self):
        self.client = APIClient()
        self.users = [
            Profile.objects.create(
                email='email1',
                last_login=datetime.utcnow()
            ),
            Profile.objects.create(
                email='email2',
                last_login=datetime.utcnow()
            )
        ]
        self.tickets = [
            Ticket.objects.create(background='test1', requester=self.users[0])
        ]
        self.attachments = [
            Attachment.objects.create(
                user=self.users[0],
                ticket=self.tickets[0],
            )
        ]

    def test_list_anonymous(self):
        response = self.client.get(reverse('attachment-list'))

        self.assertEqual(response.status_code, 401)

    def test_list_authenticated(self):
        self.client.force_authenticate(self.users[0])

        response = self.client.get(reverse('attachment-list'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            json.loads(response.content)['data'][0]['id'],
            str(self.attachments[0].id)
        )

    def test_detail_authenticated(self):
        self.client.force_authenticate(self.users[0])

        response = self.client.get(
            reverse('attachment-detail', args=[self.attachments[0].id]))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            json.loads(response.content)['data']['id'],
            str(self.attachments[0].id)
        )

    def test_detail_authenticated_without_access(self):
        self.client.force_authenticate(self.users[1])

        response = self.client.get(
            reverse('attachment-detail', args=[self.attachments[0].id]))

        self.assertEqual(response.status_code, 404)

    def test_create_authenticated(self):
        self.client.force_authenticate(self.users[0])

        attachments_count = Attachment.objects.count()

        with io.BytesIO('dummy file') as fu:
            new_data = {
                'ticket': json.dumps({
                    'type': 'tickets',
                    'id': self.tickets[0].id
                }),
                'upload': fu
            }
            response = self.client.post(
                reverse('attachment-list'),
                data=new_data,
                format='multipart',
            )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(Attachment.objects.count(), attachments_count + 1)

    def test_create_authenticated_without_access(self):
        self.client.force_authenticate(self.users[1])

        attachments_count = Attachment.objects.count()

        with io.BytesIO('dummy file') as fu:
            new_data = {
                'ticket': json.dumps({
                    'type': 'tickets',
                    'id': self.tickets[0].id
                }),
                'upload': fu
            }
            response = self.client.post(
                reverse('attachment-list'),
                data=new_data,
                format='multipart',
            )

        self.assertEqual(response.status_code, 422)
        self.assertEqual(Attachment.objects.count(), attachments_count)


class CommentsEndpointTestCase(ApiTestCase):

    def setUp(self):
        self.client = APIClient()
        self.users = [
            Profile.objects.create(
                email='email1',
                last_login=datetime.utcnow()
            ),
            Profile.objects.create(
                email='email2',
                last_login=datetime.utcnow()
            )
        ]
        self.tickets = [
            Ticket.objects.create(background='test1', requester=self.users[0])
        ]
        self.comments = [
            Comment.objects.create(
                user=self.users[0],
                ticket=self.tickets[0],
                body='first comment'
            )
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

        comments_count = Comment.objects.count()

        new_data = self.as_jsonapi_payload(
            CommentSerializer, self.comments[0], {'body': 'new comment'})

        response = self.client.post(
            reverse('comment-list'),
            data=json.dumps(new_data),
            content_type=self.JSON_API_CONTENT_TYPE
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(Comment.objects.count(), comments_count + 1)

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


class RespondersEndpointTestCase(ApiTestCase):

    def setUp(self):
        self.client = APIClient()
        self.users = [
            Profile.objects.create(
                email='email1',
                last_login=datetime.utcnow()
            ),
            Profile.objects.create(
                email='email2',
                last_login=datetime.utcnow()
            ),
            Profile.objects.create(
                email='email3',
                last_login=datetime.utcnow(),
                is_superuser=True
            )
        ]
        self.tickets = [
            Ticket.objects.create(background='test1', requester=self.users[0]),
            Ticket.objects.create(background='test1', requester=self.users[1])
        ]
        self.responders = [
            Responder.objects.create(
                ticket=self.tickets[0], user=self.users[1]),
            Responder.objects.create(
                ticket=self.tickets[1], user=self.users[2])
        ]

    def test_create_non_superuser(self):
        self.client.force_authenticate(self.users[0])

        new_data = self.as_jsonapi_payload(
            ResponderSerializer, self.responders[0])

        new_data['data']['attributes']['user']['id'] = self.users[2].id

        response = self.client.post(
            reverse('responder-list'),
            data=json.dumps(new_data),
            content_type=self.JSON_API_CONTENT_TYPE
        )

        self.assertEqual(response.status_code, 422)

    def test_create_superuser(self):
        self.client.force_authenticate(self.users[2])

        responders_count = Responder.objects.count()

        new_data = self.as_jsonapi_payload(
            ResponderSerializer, self.responders[0])

        new_data['data']['attributes']['user']['id'] = self.users[0].id

        response = self.client.post(
            reverse('responder-list'),
            data=json.dumps(new_data),
            content_type=self.JSON_API_CONTENT_TYPE
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(Responder.objects.count(), responders_count + 1)

    def test_delete_non_superuser(self):
        self.client.force_authenticate(self.users[0])

        response = self.client.delete(
            reverse('responder-detail', args=[self.responders[0].id]),
            content_type=self.JSON_API_CONTENT_TYPE
        )

        self.assertEqual(response.status_code, 404)

    def test_delete_superuser(self):
        self.client.force_authenticate(self.users[2])

        responders_count = Responder.objects.count()

        response = self.client.delete(
            reverse('responder-detail', args=[self.responders[0].id]),
            content_type=self.JSON_API_CONTENT_TYPE
        )

        self.assertEqual(response.status_code, 204)
        self.assertEqual(Responder.objects.count(), responders_count - 1)

    def test_list_anonymous(self):
        response = self.client.get(reverse('responder-list'))

        self.assertEqual(response.status_code, 401)

    def test_list_authenticated(self):
        self.client.force_authenticate(self.users[0])

        response = self.client.get(reverse('responder-list'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(json.loads(response.content)['data']), 1)
        self.assertEqual(
            json.loads(response.content)['data'][0]['id'],
            str(self.responders[0].id)
        )

    def test_get_authenticated(self):
        self.client.force_authenticate(self.users[0])

        response = self.client.get(
            reverse('responder-detail', args=[self.responders[0].id]))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            json.loads(response.content)['data']['id'],
            str(self.responders[0].id)
        )

    def test_get_authenticated_without_access(self):
        self.client.force_authenticate(self.users[0])

        response = self.client.get(
            reverse('responder-detail', args=[self.responders[1].id]))

        self.assertEqual(response.status_code, 404)
