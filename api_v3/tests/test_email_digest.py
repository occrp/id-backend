from datetime import datetime

import mock
from django.test import TestCase

from api_v3.models import Action, Profile, Comment, Ticket, Responder
from api_v3.management.commands.email_ticket_digest import Command


class TicketDigestTestCase(TestCase):

    def setUp(self):
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
            Ticket.objects.create(
                requester=self.users[0], background='ticket1'),
            Ticket.objects.create(
                requester=self.users[1], background='ticket2')
        ]

        self.responder = Responder.objects.create(
            user=self.users[1], ticket=self.tickets[0])
        self.comment = Comment.objects.create(
            ticket=self.tickets[0], user=self.users[0])

        self.actions = [
            Action.objects.create(
                verb='ticket:create',
                target=self.tickets[0],
                actor=self.users[0]
            ),
            Action.objects.create(
                verb='ticket:update:status_in-progress',
                target=self.tickets[1],
                actor=self.users[1]
            ),
            Action.objects.create(
                verb='ticket:update:reopen',
                target=self.tickets[1],
                actor=self.users[1]
            ),
            Action.objects.create(
                verb='ticket:update:pending',
                target=self.tickets[1],
                actor=self.users[1]
            ),
            Action.objects.create(
                verb='responder:create',
                target=self.tickets[0],
                actor=self.users[0],
                action=self.users[1]
            ),
            Action.objects.create(
                verb='comment:create',
                target=self.tickets[0],
                actor=self.users[0],
                action=self.comment
            )
        ]

    def test_emails(self):
        command = Command()
        email = {}
        request_host = 'test.host'

        with mock.patch.object(
                command, 'email', lambda x: (email.update(x), 1)):
            status = command.handle(request_host=request_host)

        digest1 = email[self.users[0].id]['digests']
        digest2 = email[self.users[1].id]['digests']

        self.assertIn('Sent 1 notifications', status)
        self.assertEqual(email[self.users[0].id]['user'], self.users[0])
        self.assertEqual(len(digest1), 2)
        self.assertIn(request_host, str(digest1))
        self.assertIn(request_host, str(digest2))
        self.assertIn('email1 added a comment to ticket', str(digest1))
        self.assertIn(
            'email1 added email2 as a responder to ticket', str(digest1))

        self.assertEqual(email[self.users[1].id]['user'], self.users[1])
        self.assertEqual(len(digest2), 5)
        self.assertIn('email1 added a comment to ticket', str(digest1))
        self.assertIn(
            'email1 added email2 as a responder to ticket', str(digest2))
        self.assertIn(
            'email2 updated status to in-progress to ticket', str(digest2))
        self.assertIn('email2 did reopen the ticket', str(digest2))
        self.assertIn(
            'email2 marked pending (waiting for third-party actions) '
            'the ticket',
            str(digest2)
        )
