from api_v3.factories import ProfileFactory
from api_v3.serializers import ProfileSerializer
from .support import TestCase, APIClient, reverse


class SessionsEndpointTestCase(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.users = [
            ProfileFactory.create(),
            ProfileFactory.create()
        ]

    def test_me_anonymous(self):
        response = self.client.get(reverse('me-list'))

        self.assertEqual(response.status_code, 401)

    def test_me_authenticated(self):
        self.client.force_authenticate(self.users[0])

        response = self.client.get(reverse('me-list'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.data,
            ProfileSerializer(self.users[0]).data
        )
