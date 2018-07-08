# -*- coding: utf-8 -*-
import json

from api_v3.factories import ProfileFactory
from api_v3.serializers import ProfileSerializer
from .support import ApiTestCase, APIClient, reverse


class ProfilesEndpointTestCase(ApiTestCase):

    def setUp(self):
        self.client = APIClient()
        self.users = [
            ProfileFactory.create(),
            ProfileFactory.create(),
            ProfileFactory.create(is_superuser=True),
        ]

    def test_list_anonymous(self):
        response = self.client.get(reverse('profile-list'))

        self.assertEqual(response.status_code, 401)

    def test_list_authenticated_no_staff_or_superuser(self):
        self.client.force_authenticate(self.users[0])

        response = self.client.get(reverse('profile-list'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.users[0].email)
        self.assertNotContains(response, self.users[1].email)
        self.assertNotContains(response, self.users[2].email)

    def test_list_authenticated_not_superuser(self):
        self.users[0].is_staff = True
        self.users[0].save()
        self.users[1].is_superuser = True
        self.users[1].save()
        self.client.force_authenticate(self.users[0])

        response = self.client.get(reverse('profile-list'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.users[0].email)
        self.assertNotContains(response, self.users[1].email)
        self.assertNotContains(response, self.users[2].email)

    def test_list_authenticated_superuser(self):
        self.users[0].is_staff = True
        self.users[0].save()
        self.users[1].is_superuser = True
        self.users[1].save()
        self.client.force_authenticate(self.users[2])

        response = self.client.get(reverse('profile-list'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.users[0].email)
        self.assertContains(response, self.users[1].email)
        self.assertContains(response, self.users[2].email)

    def test_list_search_authenticated(self):
        self.users[0].is_staff = True
        self.users[0].save()
        self.users[1].is_staff = True
        self.users[1].save()
        self.client.force_authenticate(self.users[2])

        response = self.client.get(
            reverse('profile-list'), {
                'filter[name]': self.users[1].first_name[1:4]
            }
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.users[1].email)
        self.assertNotContains(response, self.users[0].email)
        self.assertNotContains(response, self.users[2].email)

    def test_list_search_unicode_authenticated(self):
        self.users[0].first_name = u'Станислав'
        self.users[0].is_staff = True
        self.users[0].save()
        self.users[1].last_name = u'Sușcov'
        self.users[1].is_staff = True
        self.users[1].save()
        self.client.force_authenticate(self.users[2])

        response = self.client.get(
            reverse('profile-list'), {
                'filter[name]': self.users[0].first_name[1:4]
            }
        )

        self.assertEqual(response.status_code, 200)

        content = response.content.decode('utf8')

        self.assertIn(self.users[0].email, content)
        self.assertIn(self.users[0].first_name, content)
        self.assertNotIn(self.users[1].email, content)

        response = self.client.get(
            reverse('profile-list'), {
                'filter[name]': self.users[1].last_name[1:4]
            }
        )

        self.assertEqual(response.status_code, 200)

        content = response.content.decode('utf8')

        self.assertIn(self.users[1].email, content)
        self.assertIn(self.users[1].last_name, content)
        self.assertNotIn(self.users[0].email, content)

    def test_update_authenticated_not_owned_profile(self):
        self.client.force_authenticate(self.users[0])

        new_data = self.as_jsonapi_payload(
            ProfileSerializer, self.users[1], {'bio': 'Short Bio'})

        response = self.client.patch(
            reverse('profile-detail', args=[self.users[1].id]),
            data=json.dumps(new_data),
            content_type=ApiTestCase.JSON_API_CONTENT_TYPE
        )

        self.assertEqual(response.status_code, 404)

    def test_update_authenticated(self):
        self.users[0].is_staff = False
        self.users[0].save()
        self.client.force_authenticate(self.users[0])

        email = 'ignored@email.address'
        new_data = self.as_jsonapi_payload(
            ProfileSerializer, self.users[0], {
                'email': email, 'bio': 'Short Bio', 'is_staff': True})

        response = self.client.patch(
            reverse('profile-detail', args=[self.users[0].id]),
            data=json.dumps(new_data),
            content_type=ApiTestCase.JSON_API_CONTENT_TYPE
        )

        self.assertEqual(response.status_code, 200)

        data = json.loads(response.content)['data']

        self.assertNotEqual(data['attributes']['email'], email)
        self.assertEqual(data['attributes']['bio'], u'Short Bio')
        self.assertFalse(data['attributes']['is-staff'])

    def test_update_authenticated_superuser(self):
        self.users[0].is_staff = False
        self.users[0].save()
        self.client.force_authenticate(self.users[2])

        email = 'ignored@email.address'
        new_data = self.as_jsonapi_payload(
            ProfileSerializer, self.users[0], {
                'email': email, 'bio': 'Short Bio', 'is_staff': True})

        response = self.client.patch(
            reverse('profile-detail', args=[self.users[0].id]),
            data=json.dumps(new_data),
            content_type=ApiTestCase.JSON_API_CONTENT_TYPE
        )

        self.assertEqual(response.status_code, 200)

        data = json.loads(response.content)['data']

        self.assertNotEqual(data['attributes']['email'], email)
        self.assertEqual(data['attributes']['bio'], u'Short Bio')
        self.assertTrue(data['attributes']['is-staff'])
