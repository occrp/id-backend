from django.test import TestCase
from django.contrib.auth.models import AnonymousUser#, User
from django.contrib.auth import get_user_model # as per https://docs.djangoproject.com/en/dev/topics/auth/customizing/#referencing-the-user-model

class UserTestCase(TestCase):
    def setUp(self):
        self.anonymous_user = AnonymousUser()
        
        self.normal_user = get_user_model().objects.create_user(
            email='testuser@occrp.org', password='top_secret')
        self.normal_user.is_user = True
        self.normal_user.save()

        self.volunteer_user = get_user_model().objects.create_user(
            email='testvolunteer@occrp.org', password='top_secret')
        self.volunteer_user.is_volunteer = True
        self.volunteer_user.save()

        self.staff_user = get_user_model().objects.create_user(
            email='teststaff@occrp.org', password='top_secret')
        self.staff_user.is_staff = True
        self.staff_user.save()

        self.admin_user = get_user_model().objects.create_user(
            email='testsuperuser@occrp.org', password='top_secret')
        self.admin_user.is_superuser = True
        self.admin_user.save()

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

