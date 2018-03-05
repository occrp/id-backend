from datetime import datetime

from django.test import TestCase
import mock

from api_v3.models import Action, Responder
from api_v3.management.commands import email_ticket_digest
from api_v3.factories import TicketFactory, CommentFactory


class TicketDigestTestCase(TestCase):

    def setUp(self):
        self.tickets = [
            TicketFactory.create(deadline_at=datetime.utcnow()),
            TicketFactory.create(),
        ]

        self.users = [
            self.tickets[0].requester,
            self.tickets[1].requester
        ]

        self.responder = Responder.objects.create(
            user=self.users[1], ticket=self.tickets[0])
        self.comment = CommentFactory.create(
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

    def test_email_rendering(self):
        command = email_ticket_digest.Command()
        emails = []
        request_host = 'test.host'

        with mock.patch.object(
            email_ticket_digest,
            'send_mass_mail',
            lambda x, fail_silently: (emails.extend(x), 1)
        ):
            command.handle(request_host=request_host)

        self.assertEqual(len(emails), 2)
        self.assertEqual(len(emails[0]), 4)
        self.assertEqual(len(emails[1]), 4)

    def test_emails(self):
        command = email_ticket_digest.Command()
        email = {}
        request_host = 'test.host'

        with mock.patch.object(
                command, 'email', lambda x: (email.update(x), 1)):
            status = command.handle(request_host=request_host)

        digest1 = email[self.users[0].id]['digests']
        digest2 = email[self.users[1].id]['digests']
        upcoming1 = email[self.users[0].id]['upcoming']
        upcoming2 = email[self.users[1].id]['upcoming']

        self.assertEqual(len(upcoming1), 0)
        self.assertEqual(len(upcoming2), 1)
        self.assertIn(self.tickets[0], upcoming2)

        self.assertIn('Sent 1 notifications', status)
        self.assertEqual(email[self.users[0].id]['user'], self.users[0])
        self.assertEqual(len(digest1), 2)
        self.assertIn(request_host, str(digest1))
        self.assertIn(request_host, str(digest2))
        self.assertIn(
            u'{} added a comment to ticket'.format(self.users[0].display_name),
            u' '.join(digest1)
        )
        self.assertIn(
            u'{} added {} as a responder to ticket'.format(
                self.users[0].display_name, self.users[1].display_name
            ),
            u' '.join(digest1)
        )

        self.assertEqual(email[self.users[1].id]['user'], self.users[1])
        self.assertEqual(len(digest2), 5)
        self.assertIn(
            u'{} added a comment to ticket'.format(self.users[0].display_name),
            u' '.join(digest1)
        )
        self.assertIn(
            u'{} added {} as a responder to ticket'.format(
                self.users[0].display_name, self.users[1].display_name
            ),
            u' '.join(digest2)
        )
        self.assertIn(
            u'{} updated status to in-progress to ticket'.format(
                self.users[1].display_name
            ),
            u' '.join(digest2)
        )
        self.assertIn(
            u'{} did reopen the ticket'.format(self.users[1].display_name),
            u' '.join(digest2)
        )
        self.assertIn(
            u'{} marked pending (waiting for third-party actions) '
            u'the ticket'.format(self.users[1].display_name),
            u' '.join(digest2)
        )
