# -*- coding: utf-8 -*-

import io
import json
import os.path
from datetime import datetime, timedelta

from django.conf import settings
from django.test import TestCase
from django.core.urlresolvers import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient
from rest_framework_json_api.utils import(
    get_resource_type_from_serializer, format_keys)


from api_v3.factories import ProfileFactory, TicketFactory
from api_v3.models import(
    Ticket, Profile, Responder, Attachment, Comment, Action)
from api_v3.serializers import(
    ProfileSerializer, TicketSerializer,
    CommentSerializer, ResponderSerializer)
from api_v3.views import CommentsEndpoint, render_to_string, DEFAULT_FROM_EMAIL


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


class DownloadEndpointTestCase(TestCase):

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
                last_login=datetime.utcnow()
            )
        ]
        self.tickets = [
            Ticket.objects.create(background='test1', requester=self.users[0]),
            Ticket.objects.create(background='test1', requester=self.users[0])
        ]

        self.responder = Responder.objects.create(
            ticket=self.tickets[0], user=self.users[1])

        self.attachment = Attachment.objects.create(
            user=self.users[1],
            ticket=self.tickets[0],
            upload=SimpleUploadedFile(u'țеșт.txt', b'test')
        )

    def test_retrieve_anonymous(self):
        response = self.client.get(
            reverse('download-detail', args=[self.attachment.id]))

        self.assertEqual(response.status_code, 401)

    def test_retrieve_auth_not_ticket_user(self):
        self.client.force_authenticate(self.users[2])

        response = self.client.get(
            reverse('download-detail', args=[self.attachment.id]))

        self.assertEqual(response.status_code, 404)

    def test_retrieve_auth_ticket_requester(self):
        self.client.force_authenticate(self.users[0])

        response = self.client.get(
            reverse('download-detail', args=[self.attachment.id]))

        self.assertEqual(response.status_code, 200)
        self.assertEquals(
            response.get('Content-Disposition'),
            'filename={}'.format(os.path.basename(
                self.attachment.upload.name.encode('utf-8', 'replace')
            ))
        )

    def test_retrieve_auth_ticket_responder(self):
        self.client.force_authenticate(self.users[1])

        response = self.client.get(
            reverse('download-detail', args=[self.attachment.id]))

        self.assertEqual(response.status_code, 200)
        self.assertEquals(
            response.get('Content-Disposition'),
            'filename={}'.format(os.path.basename(
                self.attachment.upload.name.encode('utf-8', 'ignore')
            ))
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
            ),
            Profile.objects.create(
                email='email3',
                last_login=datetime.utcnow()
            ),
            Profile.objects.create(
                email='email4',
                last_login=datetime.utcnow()
            )
        ]

        self.tickets = [
            Ticket.objects.create(background='test1', requester=self.users[0]),
            Ticket.objects.create(background='test2', requester=self.users[0]),
            Ticket.objects.create(background='test3', requester=self.users[1])
        ]

        self.responders = [
            Responder.objects.create(
                ticket=self.tickets[0], user=self.users[1]),
            Responder.objects.create(
                ticket=self.tickets[0], user=self.users[2])
        ]

    def test_list_anonymous(self):
        response = self.client.get(reverse('ticket-list'))

        self.assertEqual(response.status_code, 403)

    def test_list_authenticated(self):
        self.client.force_authenticate(self.users[0])

        response = self.client.get(reverse('ticket-list'))

        self.assertEqual(response.status_code, 200)
        self.assertIn(self.tickets[0].background, response.content)

        body = json.loads(response.content)

        self.assertEqual(body['meta']['total']['all'], 2)

    def test_list_authenticated_superuser(self):
        self.users[0].is_superuser = True
        self.users[0].save()

        self.client.force_authenticate(self.users[0])

        response = self.client.get(reverse('ticket-list'))

        self.assertEqual(response.status_code, 200)
        self.assertIn(self.tickets[0].background, response.content)

        body = json.loads(response.content)

        self.assertEqual(body['meta']['total']['all'], 3)

    def test_list_authenticated_with_includes(self):
        self.client.force_authenticate(self.users[0])

        response = self.client.get(
            reverse('ticket-list'), {'include': 'requester,responders.user'})

        self.assertEqual(response.status_code, 200)
        self.assertIn('included', response.content)
        self.assertNotIn(self.responders[0].user.email, response.content)
        self.assertNotIn(self.responders[1].user.email, response.content)

    def test_list_filter_authenticated_by_responders(self):
        self.client.force_authenticate(self.users[0])

        response = self.client.get(
            reverse('ticket-list'), {
                'filter[users]': 'none'
            }
        )

        self.assertEqual(response.status_code, 200)

    def test_get_authenticated(self):
        self.client.force_authenticate(self.users[0])

        response = self.client.get(
            reverse('ticket-detail', args=[self.tickets[0].id]))

        self.assertEqual(response.status_code, 200)
        self.assertIn(self.tickets[0].background, response.content)

    def test_update_authenticated(self):
        ticket = self.tickets[0]
        self.client.force_authenticate(self.users[3])

        new_data = self.as_jsonapi_payload(
            TicketSerializer, ticket, {'background': 'new-background'})

        response = self.client.put(
            reverse('ticket-detail', args=[ticket.id]),
            data=json.dumps(new_data),
            content_type=self.JSON_API_CONTENT_TYPE
        )

        self.assertEqual(response.status_code, 404)

    def test_update_authenticated_author(self):
        ticket = self.tickets[0]
        self.client.force_authenticate(self.tickets[0].requester)

        new_data = self.as_jsonapi_payload(
            TicketSerializer, ticket, {'status': 'closed'})

        response = self.client.put(
            reverse('ticket-detail', args=[ticket.id]),
            data=json.dumps(new_data),
            content_type=self.JSON_API_CONTENT_TYPE
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            Ticket.objects.get(id=self.tickets[0].id).status, 'closed')

    def test_update_authenticated_responder(self):
        ticket = self.tickets[0]
        self.client.force_authenticate(self.users[2])

        new_data = self.as_jsonapi_payload(
            TicketSerializer, ticket, {'status': 'closed'})

        response = self.client.put(
            reverse('ticket-detail', args=[ticket.id]),
            data=json.dumps(new_data),
            content_type=self.JSON_API_CONTENT_TYPE
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            Ticket.objects.get(id=self.tickets[0].id).status, 'closed')

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

        response = self.client.patch(
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
        self.assertEqual(action.verb, 'ticket:update:reopen')
        self.assertEqual(action.action, comment)

    def test_update_authenticated_invalid_deadline(self):
        ticket = self.tickets[0]
        user = self.users[1]
        self.client.force_authenticate(user)

        new_data = self.as_jsonapi_payload(
            TicketSerializer, ticket, {
                'deadline_at': '1900-01-01T00:00',
            })

        response = self.client.patch(
            reverse('ticket-detail', args=[ticket.id]),
            data=json.dumps(new_data),
            content_type=self.JSON_API_CONTENT_TYPE
        )

        self.assertEqual(response.status_code, 422)

        reloaded_ticket = Ticket.objects.get(id=ticket.id)

        self.assertEqual(reloaded_ticket.deadline_at, ticket.deadline_at)

        response = json.loads(response.content)
        self.assertEqual(
            response['errors'][0]['detail']['data/attributes/deadline_at'],
            'The date can not be in the past.'
        )

    def test_update_authenticated_responder_pending_reason(self):
        ticket = self.tickets[0]
        user = self.users[1]
        self.client.force_authenticate(user)

        the_reason = 'The reason...'

        new_data = self.as_jsonapi_payload(
            TicketSerializer, ticket, {
                'status': 'pending',
                'pending_reason': the_reason
            })

        response = self.client.patch(
            reverse('ticket-detail', args=[ticket.id]),
            data=json.dumps(new_data),
            content_type=self.JSON_API_CONTENT_TYPE
        )

        self.assertEqual(response.status_code, 200)

        ticket = Ticket.objects.get(id=ticket.id)
        comment = ticket.comments.first()
        action = Action.objects.filter(target_object_id=str(ticket.id)).first()

        self.assertEqual(ticket.status, 'pending')
        self.assertEqual(ticket.comments.count(), 1)
        self.assertEqual(comment.body, the_reason)
        self.assertEqual(action.verb, 'ticket:update:pending')
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
            ),
            Profile.objects.create(
                first_name='Super',
                last_name='User',
                email='email3',
                last_login=datetime.utcnow(),
                is_superuser=True
            )
        ]

    def test_list_anonymous(self):
        response = self.client.get(reverse('profile-list'))

        self.assertEqual(response.status_code, 403)

    def test_list_authenticated_no_staff_or_superuser(self):
        self.client.force_authenticate(self.users[0])

        response = self.client.get(reverse('profile-list'))

        self.assertEqual(response.status_code, 200)
        self.assertIn(self.users[0].email, response.content)
        self.assertNotIn(self.users[1].email, response.content)
        self.assertNotIn(self.users[2].email, response.content)

    def test_list_authenticated_not_superuser(self):
        self.users[0].is_staff = True
        self.users[0].save()
        self.users[1].is_superuser = True
        self.users[1].save()
        self.client.force_authenticate(self.users[0])

        response = self.client.get(reverse('profile-list'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.users[0].email, response.content)
        self.assertNotIn(self.users[1].email, response.content)
        self.assertNotIn(self.users[2].email, response.content)

    def test_list_authenticated_superuser(self):
        self.users[0].is_staff = True
        self.users[0].save()
        self.users[1].is_superuser = True
        self.users[1].save()
        self.client.force_authenticate(self.users[2])

        response = self.client.get(reverse('profile-list'))

        self.assertEqual(response.status_code, 200)
        self.assertIn(self.users[0].email, response.content)
        self.assertIn(self.users[1].email, response.content)
        self.assertIn(self.users[2].email, response.content)

    def test_list_search_authenticated(self):
        self.users[0].is_staff = True
        self.users[0].save()
        self.users[1].is_staff = True
        self.users[1].save()
        self.client.force_authenticate(self.users[2])

        response = self.client.get(
            reverse('profile-list'), {
                'filter[name]': self.users[1].first_name[1:4]
            }
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn(self.users[1].email, response.content)
        self.assertNotIn(self.users[0].email, response.content)
        self.assertNotIn(self.users[2].email, response.content)

    def test_list_search_unicode_authenticated(self):
        self.users[0].first_name = u'Станислав'
        self.users[0].is_staff = True
        self.users[0].save()
        self.users[1].last_name = u'Sușcov'
        self.users[1].is_staff = True
        self.users[1].save()
        self.client.force_authenticate(self.users[2])

        response = self.client.get(
            reverse('profile-list'), {
                'filter[name]': self.users[0].first_name[1:4]
            }
        )

        self.assertEqual(response.status_code, 200)

        content = response.content.decode('utf8')

        self.assertIn(self.users[0].email, content)
        self.assertIn(self.users[0].first_name, content)
        self.assertNotIn(self.users[1].email, content)

        response = self.client.get(
            reverse('profile-list'), {
                'filter[name]': self.users[1].last_name[1:4]
            }
        )

        self.assertEqual(response.status_code, 200)

        content = response.content.decode('utf8')

        self.assertIn(self.users[1].email, content)
        self.assertIn(self.users[1].last_name, content)
        self.assertNotIn(self.users[0].email, content)

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

        self.assertEqual(response.status_code, 403)

    def test_list_authenticated_no_tickets(self):
        self.client.force_authenticate(self.users[0])

        response = self.client.get(reverse('action-list'))

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
                upload=SimpleUploadedFile(u'tesț.txt', b'tesț')
            )
        ]

    def test_list_anonymous(self):
        response = self.client.get(reverse('attachment-list'))

        self.assertEqual(response.status_code, 403)

    def test_list_authenticated(self):
        self.client.force_authenticate(self.users[0])

        response = self.client.get(reverse('attachment-list'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            json.loads(response.content)['data'][0]['id'],
            str(self.attachments[0].id)
        )

        self.assertIn(
            reverse('download-detail', args=[self.attachments[0].id]),
            response.content.decode('utf-8')
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

        ticket = self.tickets[0]
        attachments_count = Attachment.objects.count()
        actions_count = Action.objects.filter(
            target_object_id=ticket.id).count()

        with io.BytesIO(b'dummy file') as fu:
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

        serializer_data = json.loads(response.content)['data']

        self.assertEqual(response.status_code, 201)
        self.assertIn(
            reverse('download-detail', args=[serializer_data['id']]),
            serializer_data['attributes']['upload']
        )
        self.assertEqual(Attachment.objects.count(), attachments_count + 1)
        self.assertEqual(
            Action.objects.filter(
                target_object_id=ticket.id,
                verb='attachment:create'
            ).count(),
            actions_count + 1
        )

    def test_create_authenticated_without_access(self):
        self.client.force_authenticate(self.users[1])

        attachments_count = Attachment.objects.count()

        with io.BytesIO(b'dummy file') as fu:
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
            ),
            Profile.objects.create(
                email='email3',
                last_login=datetime.utcnow()
            ),
            Profile.objects.create(
                email='email4',
                last_login=datetime.utcnow()
            )
        ]
        self.tickets = [
            Ticket.objects.create(background='test1', requester=self.users[0])
        ]
        self.responders = [
            Responder.objects.create(
                ticket=self.tickets[0], user=self.users[2]),
            Responder.objects.create(
                ticket=self.tickets[0], user=self.users[3])
        ]
        self.comments = [
            Comment.objects.create(
                user=self.users[3],
                ticket=self.tickets[0],
                body='first comment'
            )
        ]

    def test_list_anonymous(self):
        response = self.client.get(reverse('comment-list'))

        self.assertEqual(response.status_code, 403)

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
        controller = CommentsEndpoint()
        count, emails = controller.email_notify(self.comments[0])

        self.assertEqual(count, 2)
        self.assertEqual(emails[0], [
            controller.EMAIL_SUBJECT.format(self.tickets[0].id),
            render_to_string(
                'mail/ticket_comment.txt',
                dict(comment=self.comments[0], name='email3')
            ),
            DEFAULT_FROM_EMAIL,
            ['email3']
        ])
        self.assertEqual(emails[1], [
            controller.EMAIL_SUBJECT.format(self.tickets[0].id),
            render_to_string(
                'mail/ticket_comment.txt',
                dict(comment=self.comments[0], name='email1')
            ),
            DEFAULT_FROM_EMAIL,
            ['email1']
        ])


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

        # Set to initial ticket status
        self.tickets[0].status = Ticket.STATUSES[0][0]
        self.tickets[0].save()

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
        self.assertEqual(
            Ticket.objects.get(id=self.tickets[0].id).status,
            Ticket.STATUSES[1][0]
        )

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

        self.assertEqual(response.status_code, 403)

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

        self.tickets[0].created_at=(datetime.utcnow() - timedelta(days=5))
        self.tickets[0].save()

        self.responders = [
            Responder.objects.create(
                ticket=self.tickets[0], user=self.users[1]),
            Responder.objects.create(
                ticket=self.tickets[1], user=self.users[1]),
            Responder.objects.create(
                ticket=self.tickets[1], user=self.users[2])
        ]

    def test_list_anonymous(self):
        response = self.client.get(reverse('ticket_stats-list'))

        self.assertEqual(response.status_code, 403)

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

        self.assertEqual(len(body['meta']['total']), 9)
        self.assertEqual(body['meta']['total']['new'], 4)
        self.assertEqual(body['meta']['total']['open'], 4)
        self.assertEqual(body['meta']['total']['cancelled'], 1)
        self.assertEqual(body['meta']['total']['resolved'], 1)

        self.assertEqual(
            sorted(body['meta']['staff-profile-ids']),
            sorted([self.users[1].id, self.users[2].id])
        )
        self.assertEqual(
            body['meta']['countries'],
            sorted(set(map(lambda t: t.country, self.tickets)))
        )
        self.assertEqual(len(body['data']), 2)

        self.assertEqual(body['data'][0]['attributes']['count'], 1)
        self.assertEqual(body['data'][0]['attributes']['status'], 'cancelled')
        self.assertEqual(body['data'][0]['attributes']['avg-time'], 5)
        self.assertEqual(body['data'][0]['attributes']['past-deadline'], 1)
        self.assertEqual(
            body['data'][0]['attributes']['date'],
            datetime.utcnow().replace(
                day=1, hour=0, minute=0, second=0, microsecond=0).isoformat()
        )

        self.assertEqual(body['data'][1]['attributes']['count'], 4)
        self.assertEqual(body['data'][1]['attributes']['status'], 'new')
        self.assertEqual(body['data'][1]['attributes']['avg-time'], 0)
        self.assertEqual(body['data'][1]['attributes']['past-deadline'], 0)
        self.assertEqual(
            body['data'][1]['attributes']['date'],
            datetime.utcnow().replace(
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
            datetime.utcnow().replace(day=1) - timedelta(days=28*3))

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

        self.assertEqual(len(body['meta']['total']), 9)
        self.assertEqual(body['meta']['total']['new'], 1)
        self.assertEqual(body['meta']['total']['open'], 1)
        self.assertEqual(body['meta']['total']['cancelled'], 1)
        self.assertEqual(body['meta']['total']['resolved'], 1)

        self.assertEqual(body['meta']['staff-profile-ids'], [])
        self.assertEqual(body['meta']['countries'], [])

        self.assertEqual(len(body['data']), 2)

        self.assertNotEqual(body['data'][0]['id'], body['data'][1]['id'])

        self.assertEqual(body['data'][0]['attributes']['count'], 1)
        self.assertEqual(body['data'][0]['attributes']['status'], 'cancelled')
        self.assertEqual(body['data'][0]['attributes']['avg-time'], 5)
        self.assertEqual(body['data'][0]['attributes']['past-deadline'], 1)
        self.assertEqual(
            body['data'][0]['attributes']['date'],
            datetime.utcnow().replace(
                day=1, hour=0, minute=0, second=0, microsecond=0).isoformat()
        )

        self.assertEqual(body['data'][1]['attributes']['count'], 1)
        self.assertEqual(body['data'][1]['attributes']['status'], 'new')
        self.assertEqual(body['data'][1]['attributes']['avg-time'], 0)
        self.assertEqual(body['data'][1]['attributes']['past-deadline'], 0)
        self.assertEqual(
            body['data'][1]['attributes']['date'],
            datetime.utcnow().replace(
                day=1, hour=0, minute=0, second=0, microsecond=0).isoformat()
        )
