# -*- coding: utf-8 -*-
import os.path

from django.core.files.uploadedfile import SimpleUploadedFile

from api_v3.factories import (
    AttachmentFactory,
    ProfileFactory,
    ResponderFactory,
    TicketFactory
)
from .support import TestCase, APIClient, reverse


class DownloadEndpointTestCase(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.users = [
            ProfileFactory.create(),
            ProfileFactory.create(),
            ProfileFactory.create()
        ]
        self.tickets = [
            TicketFactory.create(requester=self.users[0]),
            TicketFactory.create(requester=self.users[0])
        ]

        self.responder = ResponderFactory.create(
            ticket=self.tickets[0], user=self.users[1])

        self.attachment = AttachmentFactory.create(
            user=self.users[1],
            ticket=self.tickets[0],
            upload=SimpleUploadedFile('țеșт.txt', b'test')
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
        self.assertEqual(
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
        self.assertEqual(
            response.get('Content-Disposition'),
            'filename={}'.format(os.path.basename(
                self.attachment.upload.name.encode('utf-8', 'ignore')
            ))
        )
