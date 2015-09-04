from django.core.urlresolvers import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase


class SearchAPITest(APITestCase):
    fixtures = ['id/fixtures/initial_data.json']

    def setUp(self):
        super(SearchAPITest, self).setUp()

        user = get_user_model().objects
        self.staff_user = user.get(email='staff@example.com')
        self.admin_user = user.get(email='admin@example.com')
        self.user_user = user.get(email='user@example.com')
        self.other_user = user.get(email='user2@example.com')

    def tearDown(self):
        super(SearchAPITest, self).tearDown()

    def test_trigger_document_search(self):
        url = reverse('search_documents_query')
        res = self.client.get(url, {'q': 'foo'})
        self.assertEqual(res.status_code, 200)
