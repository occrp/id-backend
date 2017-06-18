from datetime import datetime

from django.test import TestCase

from api_v3.models import Ticket, Profile, Responder, Attachment, Comment


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
            )
        ]

        self.tickets = [
            Ticket.objects.create(background='test1', requester=self.users[0]),
            Ticket.objects.create(background='test2', requester=self.users[1])
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

    def test_attachment_filter_by_user(self):
        attachments = Attachment.filter_by_user(self.users[0])

        self.assertEqual(attachments.count(), 3)
        self.assertIn(self.attachments[0], attachments)
        self.assertIn(self.attachments[1], attachments)
        self.assertIn(self.attachments[2], attachments)

    def test_comment_filter_by_user(self):
        comments = Comment.filter_by_user(self.users[0])

        self.assertEqual(comments.count(), 3)
        self.assertIn(self.comments[0], comments)
        self.assertIn(self.comments[1], comments)
        self.assertIn(self.comments[2], comments)


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

        self.assertEqual(attachments.count(), 4)

        for attachment in self.attachments:
            self.assertIn(attachment, attachments)

    def test_comment_filter_by_user(self):
        comments = Comment.filter_by_user(self.users[0])

        self.assertEqual(comments.count(), 4)

        for comment in self.comments:
            self.assertIn(comment, comments)
