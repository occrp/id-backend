from .support import TestCase, APIClient, reverse


class AuthEndpointTestCase(TestCase):

    def setUp(self):
        self.client = APIClient()

    def test_logout(self):
        response = self.client.get(reverse('logout-list'))

        self.assertEqual(response.status_code, 302)

    def test_login(self):
        response = self.client.get(reverse('login-list'))

        self.assertEqual(response.status_code, 302)
