import json

from django.test import TestCase
from django.contrib.auth.models import AnonymousUser#, User
from django.contrib.auth import get_user_model # as per https://docs.djangoproject.com/en/dev/topics/auth/customizing/#referencing-the-user-model
from django.core.urlresolvers import reverse

from .testclient import APITestClient


class UserTestCase(TestCase):
    def anon_user_helper(self):
        return AnonymousUser()

    def user_helper(self, email, **kwargs):
        return get_user_model().objects.create_user(email=email, password='top_secret', **kwargs)

    def setUp(self):
        self.anonymous_user = AnonymousUser()
        self.normal_user = self.user_helper('testuser@occrp.org')
        self.staff_user = self.user_helper('teststaff@occrp.org', is_staff=True)
        self.admin_user = self.user_helper('testsuperuser@occrp.org', is_superuser=True)

    def tearDown(self):
        pass


class APITestCase(TestCase):
    def http_action(self, verb, urlname, user, urlargs={}, data={}):
        client = APITestClient()
        if user:
            client.login_user(user)
        url = reverse(urlname, kwargs=urlargs)
        fun = getattr(client, verb)
        if verb in ["post", "put", "delete", "patch"]:
            res = fun(url, json.dumps(data), content_type='application/json')
        else:
            res = fun(url, data)
        try:
            res.json = json.loads(res.content)
        except Exception as e:
            print e

        return res

    def post(self, urlname, user=None, urlargs={}, data={}):
        return self.http_action("post", urlname, user, urlargs, data)

    def get(self, urlname, user=None, urlargs={}, data={}):
        return self.http_action("get", urlname, user, urlargs, data)

    def put(self, urlname, user=None, urlargs={}, data={}):
        return self.http_action("put", urlname, user, urlargs, data)

    def delete(self, urlname, user=None, urlargs={}, data={}):
        return self.http_action("delete", urlname, user, urlargs, data)

    def patch(self, urlname, user=None, urlargs={}, data={}):
        return self.http_action("patch", urlname, user, urlargs, data)


class CoreUtilsTest(TestCase):
    def test_listchannels(self):
        from core.models import all_known_channels
        m = all_known_channels()


class CoreAPIv2Test(APITestCase, UserTestCase):
    def test_profile(self):
        m = self.get('api_2_profile', user=self.normal_user)
        self.assertEqual(m.status_code, 200)
        self.assertIn('email', m.json)
        self.assertIn('is_admin', m.json)
        self.assertIn('groups', m.json)
        self.assertIn('display_name', m.json)
        self.assertIn('notification_subscriptions', m.json)
        self.assertIn('notifications_unseen', m.json)
        self.assertIn('locale', m.json)
        self.assertIn('id', m.json)
        self.assertEqual(m.json['email'], self.normal_user.email)
        # FIXME: need to test code path where user is a member of a network

    def test_profile_bullshit_user(self):
        m = self.get('api_2_profile')
        self.assertEqual(m.status_code, 401)
        self.assertIn('detail', m.json)

    def test_notification_subscriptions_check_none(self):
        # Check that (new) user isn't subscribed to anything:
        m = self.get('api_2_notifications', user=self.normal_user)
        self.assertEqual(m.status_code, 200)
        self.assertIn('notification_subscriptions', m.json)
        self.assertEqual(m.json['notification_subscriptions'], [])

    def test_notification_subscriptions_subscribe_none(self):
        # Try subscribing to unspecified channel:
        m = self.put('api_2_notifications', user=self.normal_user)
        self.assertEqual(m.status_code, 400)
        self.assertIn("error", m.json)

    def test_notification_subscriptions_subscribe_erroneous(self):
        # Try subscribing to erroneous channel:
        m = self.put('api_2_notifications', data={'channel': 'foo'}, user=self.normal_user)
        self.assertEqual(m.status_code, 400)
        self.assertIn("error", m.json)

    def test_notification_subscriptions_subscribe_valid_and_verify(self):
        # Try subscribing to valid channel:
        m = self.put('api_2_notifications', data={'channel': 'id:*:*:*:*'}, user=self.normal_user)
        self.assertEqual(m.status_code, 200)
        self.assertIn("result", m.json)
        self.assertEqual(m.json["result"], "subscribed")

        # Verify subscription
        m = self.get('api_2_notifications', user=self.normal_user)
        self.assertEqual(m.status_code, 200)
        self.assertIn('notification_subscriptions', m.json)
        self.assertEqual(m.json['notification_subscriptions'], ['id:*:*:*:*'])

        # Try unsubscribing from valid channel
        m = self.delete('api_2_notifications', data={'channel': 'id:*:*:*:*'}, user=self.normal_user)
        self.assertEqual(m.status_code, 200)
        self.assertIn("found", m.json)
        self.assertEqual(m.json["found"], 1)
        self.assertIn("result", m.json)
        self.assertEqual(m.json["result"], "unsubscribed")

        # Double unsubscribing should result in soft fail:
        m = self.delete('api_2_notifications', data={'channel': 'id:*:*:*:*'}, user=self.normal_user)
        self.assertEqual(m.status_code, 200)
        self.assertIn("found", m.json)
        self.assertEqual(m.json["found"], 0)
        self.assertIn("result", m.json)
        self.assertEqual(m.json["result"], "none")

    def test_notification_subscriptions_unsubscribe_invalid(self):
        # Try unsubscribing from invalid channel
        m = self.delete('api_2_notifications', data={'channel': 'foo'}, user=self.normal_user)
        self.assertEqual(m.status_code, 400)
        self.assertIn("error", m.json)

    def test_notification_subscriptions_unsubscribe_none(self):
        # Not supplying a channel is... weird. I am a teapot!
        m = self.delete('api_2_notifications', user=self.normal_user)
        self.assertEqual(m.status_code, 418)

    def test_notifications(self):
        m = self.get('api_2_notifications_stream', user=self.normal_user)
        self.assertEqual(m.status_code, 200)
        self.assertIn('count', m.json)
        self.assertEqual(m.json['count'], 0)
        self.assertIn('results', m.json)
        self.assertEqual(m.json['results'], [])

        # FIXME: Notify user and test that it's working

    def test_notifications_seen(self):
        m = self.get('api_2_notifications_seen', user=self.normal_user)
        self.assertEqual(m.status_code, 200)

        # FIXME: Verify that marking notifications as seen marks them as seen
