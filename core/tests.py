from django.test import TestCase
from django.contrib.auth.models import AnonymousUser#, User
from django.contrib.auth import get_user_model # as per https://docs.djangoproject.com/en/dev/topics/auth/customizing/#referencing-the-user-model

class UserTestCase(TestCase):
    def anon_user_helper(self):
        return AnonymousUser()

    def user_helper(self, email, **kwargs):
        return get_user_model().objects.create_user(email=email, password='top_secret', **kwargs)

    def setUp(self):
        self.anonymous_user = AnonymousUser()
        self.normal_user = self.user_helper('testuser@occrp.org', is_user=True)
        self.volunteer_user = self.user_helper('testvolunteer@occrp.org', is_volunteer=True)
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
        fun(url, data)

    def post(self, urlname, user, urlargs={}, data={}):
        return self.http_action("post", urlname, user, urlargs, data)

    def get(self, urlname, user, urlargs={}, data={}):
        return self.http_action("get", urlname, user, urlargs, data)

    def put(self, urlname, user, urlargs={}, data={}):
        return self.http_action("put", urlname, user, urlargs, data)

    def delete(self, urlname, user, urlargs={}, data={}):
        return self.http_action("delete", urlname, user, urlargs, data)

    def patch(self, urlname, user, urlargs={}, data={}):
        return self.http_action("patch", urlname, user, urlargs, data)

