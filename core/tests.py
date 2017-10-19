from django.test import TestCase, Client
from django.conf import settings
from django.core.urlresolvers import reverse
from django.contrib.auth import get_user_model


class PagesTestCase(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = get_user_model().objects.create_user(
            'test@email', password='top_secret')

    def test_homepage(self):
        response = self.client.get(reverse('home'))

        self.assertEqual(response.status_code, 200)
        self.assertIn(
            reverse('tickets_home') + '/new',
            response.content.decode('utf-8', 'escape')
        )

    def test_about_id(self):
        response = self.client.get(reverse('about_id'))

        self.assertEqual(response.status_code, 200)
        self.assertIn(
            reverse('about_us'),
            response.content.decode('utf-8', 'escape')
        )

    def test_about_us(self):
        response = self.client.get(reverse('about_us'))

        self.assertEqual(response.status_code, 200)

    def test_databases_homepage_anonymous(self):
        response = self.client.get(reverse('databases:index'))

        self.assertEqual(response.status_code, 200)
        self.assertIn(
            reverse('tickets_home') + '/new',
            response.content.decode('utf-8', 'escape')
        )

    def test_tickets_homepage_anonymous(self):
        response = self.client.get(reverse('tickets_home'))

        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('tickets_home'), response.url)

    def test_tickets_homepage_authenticated(self):
        self.client.force_login(self.user, settings.AUTHENTICATION_BACKENDS[2])

        response = self.client.get(reverse('tickets_home'))

        self.assertEqual(response.status_code, 200)
        self.assertIn(
            '<div id="ember-app"></div>',
            response.content.decode('utf-8', 'escape')
        )
