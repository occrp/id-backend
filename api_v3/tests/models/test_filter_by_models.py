from datetime import datetime

from django.test import TestCase

from api_v3.models import (
    Ticket, Profile, Responder, Attachment, Comment, Subscriber
)


class TicketAttachmentCommentFactoryMixin(TestCase):

    def setUp(self):
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
            Ticket.objects.create(
                first_name='fname', background='test1', requester=self.users[0]
            ),
            Ticket.objects.create(background='test2', requester=self.users[1]),
            Ticket.objects.create(background='test3', requester=self.users[2])
        ]

        self.attachments = [
            Attachment.objects.create(
                ticket=self.tickets[0],
                user=self.users[0]
            ),
            Attachment.objects.create(
                ticket=self.tickets[0],
                user=self.users[1]
            ),
            Attachment.objects.create(
                ticket=self.tickets[1],
                user=self.users[0]
            ),
            Attachment.objects.create(
                ticket=self.tickets[1],
                user=self.users[1]
            ),
            Attachment.objects.create(
                ticket=self.tickets[0],
                user=self.users[2]
            ),
            Attachment.objects.create(
                ticket=self.tickets[1],
                user=self.users[2]
            ),
            Attachment.objects.create(
                ticket=self.tickets[2],
                user=self.users[1]
            ),
        ]

        self.comments = [
            Comment.objects.create(
                body='body1',
                ticket=self.tickets[0],
                user=self.users[0]
            ),
            Comment.objects.create(
                body='body2',
                ticket=self.tickets[0],
                user=self.users[1]
            ),
            Comment.objects.create(
                body='body3',
                ticket=self.tickets[1],
                user=self.users[0]
            ),
            Comment.objects.create(
                body='body4',
                ticket=self.tickets[1],
                user=self.users[1]
            ),
            Comment.objects.create(
                body='body5',
                ticket=self.tickets[0],
                user=self.users[2]
            ),
            Comment.objects.create(
                body='body6',
                ticket=self.tickets[1],
                user=self.users[2]
            ),
            Comment.objects.create(
                body='body7',
                ticket=self.tickets[2],
                user=self.users[1]
            ),
        ]


class TicketAttachmentCommentFilterByUserRequesterTestCase(
        TicketAttachmentCommentFactoryMixin):

    def setUp(self):
        super(
            TicketAttachmentCommentFilterByUserRequesterTestCase, self).setUp()

    def test_tickets_filter_by_user(self):
        tickets = Ticket.filter_by_user(self.users[0])

        self.assertEqual(tickets.count(), 1)
        self.assertIn(self.tickets[0], tickets)

        tickets = Ticket.filter_by_user(self.users[0], Ticket.objects.none())
        self.assertEqual(tickets.count(), 0)

    def test_tickets_search_for(self):
        tickets = Ticket.search_for('fname')

        self.assertEqual(tickets.count(), 1)
        self.assertIn(self.tickets[0], tickets)

        tickets = Ticket.search_for('fname', Ticket.objects.none())
        self.assertEqual(tickets.count(), 0)

    def test_tickets_search_for_comments(self):
        tickets = Ticket.search_for('body1')

        self.assertEqual(tickets.count(), 1)
        self.assertIn(self.tickets[0], tickets)

    def test_attachment_filter_by_user(self):
        attachments = Attachment.filter_by_user(self.users[0])

        self.assertEqual(attachments.count(), 3)
        self.assertIn(self.attachments[0], attachments)
        self.assertIn(self.attachments[1], attachments)
        self.assertIn(self.attachments[4], attachments)

        attachments = Attachment.filter_by_user(
            self.users[0], Attachment.objects.none())
        self.assertEqual(attachments.count(), 0)

    def test_comment_filter_by_user(self):
        comments = Comment.filter_by_user(self.users[0])

        self.assertEqual(comments.count(), 3)
        self.assertIn(self.comments[0], comments)
        self.assertIn(self.comments[1], comments)
        self.assertIn(self.comments[4], comments)

        comments = Comment.filter_by_user(self.users[0], Comment.objects.none())
        self.assertEqual(comments.count(), 0)


class TicketAttachmentCommentFilterByUserResponderTestCase(
        TicketAttachmentCommentFactoryMixin):

    def setUp(self):
        super(
            TicketAttachmentCommentFilterByUserResponderTestCase, self).setUp()

        Responder.objects.create(ticket=self.tickets[1], user=self.users[0])

    def test_tickets_filter_by_user(self):
        tickets = Ticket.filter_by_user(self.users[0])

        self.assertEqual(tickets.count(), 2)
        self.assertIn(self.tickets[0], tickets)
        self.assertIn(self.tickets[1], tickets)

    def test_attachment_filter_by_user(self):
        attachments = Attachment.filter_by_user(self.users[0])

        self.assertEqual(attachments.count(), 6)

        for attachment in self.attachments[:6]:
            self.assertIn(attachment, attachments)

    def test_comment_filter_by_user(self):
        comments = Comment.filter_by_user(self.users[0])

        self.assertEqual(comments.count(), 6)

        for comment in self.comments[:6]:
            self.assertIn(comment, comments)


class TicketAttachmentCommentFilterByUserSubscriberTestCase(
        TicketAttachmentCommentFactoryMixin):

    def setUp(self):
        super(
            TicketAttachmentCommentFilterByUserSubscriberTestCase, self).setUp()

        Subscriber.objects.create(ticket=self.tickets[1], user=self.users[0])

    def test_tickets_filter_by_user(self):
        tickets = Ticket.filter_by_user(self.users[0])

        self.assertEqual(tickets.count(), 2)
        self.assertIn(self.tickets[0], tickets)
        self.assertIn(self.tickets[1], tickets)

    def test_attachment_filter_by_user(self):
        attachments = Attachment.filter_by_user(self.users[0])

        self.assertEqual(attachments.count(), 6)

        for attachment in self.attachments[:6]:
            self.assertIn(attachment, attachments)

    def test_comment_filter_by_user(self):
        comments = Comment.filter_by_user(self.users[0])

        self.assertEqual(comments.count(), 6)

        for comment in self.comments[:6]:
            self.assertIn(comment, comments)
