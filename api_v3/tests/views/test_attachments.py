# -*- coding: utf-8 -*-
import json
import io

from django.core.files.uploadedfile import SimpleUploadedFile

from api_v3.factories import ProfileFactory, TicketFactory, AttachmentFactory
from api_v3.models import Attachment, Action
from .support import ApiTestCase, APIClient, reverse


class AttachmentsEndpointTestCase(ApiTestCase):

    def setUp(self):
        self.client = APIClient()
        self.users = [
            ProfileFactory.create(),
            ProfileFactory.create()
        ]
        self.tickets = [
            TicketFactory.create(requester=self.users[0])
        ]

        self.attachments = [
            AttachmentFactory.create(
                user=self.users[0],
                ticket=self.tickets[0],
                upload=SimpleUploadedFile(
                    'tesț.txt', bytes('tesț', encoding='utf-8')
                )
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

        response = response.json()

        self.assertEqual(response['errors'][0]['detail'], 'Ticket not found.')
        self.assertEqual(
            response['errors'][0]['source']['pointer'],
            '/data/attributes/ticket'
        )

        self.assertEqual(Attachment.objects.count(), attachments_count)

    def test_delete_non_superuser(self):
        self.client.force_authenticate(self.users[1])

        response = self.client.delete(
            reverse('attachment-detail', args=[self.attachments[0].id]),
            content_type=self.JSON_API_CONTENT_TYPE
        )

        self.assertEqual(response.status_code, 404)

    def test_delete_superuser(self):
        self.users[1].is_superuser = True
        self.users[1].save()
        attachments_count = Attachment.objects.count()
        actions_count = Action.objects.filter(
            target_object_id=self.tickets[0].id,
            verb='attachment:destroy'
        ).count()

        self.client.force_authenticate(self.users[1])

        response = self.client.delete(
            reverse('attachment-detail', args=[self.attachments[0].id]),
            content_type=self.JSON_API_CONTENT_TYPE
        )

        self.assertEqual(response.status_code, 204)
        self.assertEqual(Attachment.objects.count(), attachments_count - 1)
        self.assertEqual(
            Action.objects.filter(
                target_object_id=self.tickets[0].id,
                verb='attachment:destroy'
            ).count(),
            actions_count + 1
        )

    def test_delete_attachment_author(self):
        attachments_count = Attachment.objects.count()
        actions_count = Action.objects.filter(
            target_object_id=self.tickets[0].id,
            verb='attachment:destroy'
        ).count()

        self.client.force_authenticate(self.users[0])

        response = self.client.delete(
            reverse('attachment-detail', args=[self.attachments[0].id]),
            content_type=self.JSON_API_CONTENT_TYPE
        )

        self.assertEqual(response.status_code, 204)
        self.assertEqual(Attachment.objects.count(), attachments_count - 1)
        self.assertEqual(
            Action.objects.filter(
                target_object_id=self.tickets[0].id,
                verb='attachment:destroy'
            ).count(),
            actions_count + 1
        )
