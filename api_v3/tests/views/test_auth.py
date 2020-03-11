from api_v3.factories import ProfileFactory
from .support import TestCase, APIClient, reverse


class AuthEndpointTestCase(TestCase):

    def setUp(self):
        self.client = APIClient()

    def test_login(self):
        response = self.client.get(reverse('login-list'))

        self.assertEqual(response.status_code, 302)

    def test_logout(self):
        profile = ProfileFactory.create()
        self.client.force_authenticate(profile)
        response = self.client.get(reverse('logout-detail', args=[profile.id]))

        self.assertEqual(response.status_code, 302)

    def test_logout_bad_current_user_id(self):
        response = self.client.get(reverse('logout-detail', args=['test']))

        self.assertEqual(response.status_code, 301)
