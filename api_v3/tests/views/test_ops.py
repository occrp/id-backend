from .support import TestCase, APIClient, reverse


class OpsEndpointTestCase(TestCase):

    def setUp(self):
        self.client = APIClient()

    def test_retrieve_anonymous_wrong_op_name(self):
        op_name = 'wrong-op'
        response = self.client.get(reverse('ops-detail', args=[op_name]))

        self.assertEqual(response.status_code, 200)
        self.assertNotIn(op_name, response.content)

    def test_retrieve_anonymous_good_op_name(self):
        op_name = 'email_ticket_digest'
        response = self.client.get(reverse('ops-detail', args=[op_name]))

        self.assertEqual(response.status_code, 200)
        self.assertIn(op_name, response.content)
