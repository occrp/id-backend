from django.test import TestCase

from api_v3.factories import SubscriberFactory, ProfileFactory
from api_v3.misc import oauth2
from api_v3.models import Subscriber, Action


class TicketAttachmentCommentFactoryMixin(TestCase):

    def setUp(self):
        self.new_user = ProfileFactory.create()
        self.subscriber = SubscriberFactory.create(
            user=None, email=self.new_user.email)

    def test_activate_user(self):
        self.new_user.is_active = False
        self.new_user.save()

        oauth2.activate_user(backend=None, user=self.new_user)

        self.assertTrue(self.new_user.is_active)

    def test_map_email_to_subscriber(self):
        activities = Action.objects.filter(verb='subscriber:update:joined')

        activities_count = activities.count()

        oauth2.map_email_to_subscriber(
            backend=None, user=self.new_user)

        subscriber = Subscriber.objects.get(id=self.subscriber.id)

        self.assertEqual(activities.count(), activities_count + 1)
        self.assertEqual(subscriber.user, self.new_user)
        self.assertIsNone(subscriber.email)

        oauth2.map_email_to_subscriber(
            backend=None, user=self.new_user)

        self.assertEqual(activities.count(), activities_count + 1)
