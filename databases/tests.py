from django.test import TestCase
from core.tests import APITestCase, UserTestCase



class DatabaseAPIv2Test(APITestCase, UserTestCase):
    def test_list_databases(self):
        m = self.get('api_2_databases_collection', user=self.normal_user)
        self.assertEqual(m.status_code, 200)
        self.assertIn('results', m.json)

    def test_add_database_unauthorized(self):
        post = {
            'agency': 'Test',
            'db_type': 'ip',
            'country': 'EE',
            'paid': True,
            'registration_required': False,
            'government_db': False,
            'url': 'https://database.example.com/testdatabaseuri',
            'notes': 'Nothing to speak of',
            'blog_post': '',
            'video_url': '',
        }
        m = self.post('api_2_databases_collection', user=self.normal_user, data=post)
        self.assertEqual(m.status_code, 403)

    def test_add_database_fail_missing_params(self):
        post = {
            'agency': 'Test',
        }
        m = self.post('api_2_databases_collection', user=self.admin_user, data=post)
        self.assertEqual(m.status_code, 400)

    def test_add_database_fail_invalid_params(self):
        post = {
            'agency': 'Test',
            'db_type': 'bullshit type',
            'country': 'EE',
            'paid': True,
            'registration_required': False,
            'government_db': False,
            'url': 'https://database.example.com/testdatabaseuri',
            'notes': 'Nothing to speak of',
            'blog_post': '',
            'video_url': '',
        }
        m = self.post('api_2_databases_collection', user=self.admin_user, data=post)
        self.assertEqual(m.status_code, 400)

    def test_add_database(self):
        post = {
            'agency': 'Test',
            'db_type': 'ip',
            'country': 'EE',
            'paid': True,
            'registration_required': False,
            'government_db': False,
            'url': 'https://database.example.com/testdatabaseuri',
            'notes': 'Nothing to speak of',
            'blog_post': '',
            'video_url': '',
        }
        m = self.post('api_2_databases_collection', user=self.admin_user, data=post)
        self.assertEqual(m.status_code, 201)
        self.assertIn('agency', m.json)
        r = m.json
        del r["id"]
        self.assertEqual(m.json, post)

    def test_edit_database(self):
        post = {
            'agency': 'Test',
            'db_type': 'ip',
            'country': 'EE',
            'paid': True,
            'registration_required': False,
            'government_db': False,
            'url': 'https://database.example.com/testdatabaseuri',
            'notes': 'Nothing to speak of',
            'blog_post': '',
            'video_url': '',
        }
        # First, create it:
        m = self.post('api_2_databases_collection', user=self.admin_user, data=post)
        self.assertEqual(m.status_code, 201)

        # Next, update it:
        post = m.json
        post['agency'] = 'New test agency'
        urlargs = {'pk': m.json['id']}
        m = self.put('api_2_databases_member', user=self.admin_user, urlargs=urlargs,
                     data=post)
        self.assertEqual(m.status_code, 200)
        self.assertIn('id', m.json)
        self.assertEqual(m.json, post)

    def test_delete_database(self):
        post = {
            'id': 1,
            'agency': 'Test',
            'db_type': 'ip',
            'country': 'EE',
            'paid': True,
            'registration_required': False,
            'government_db': False,
            'url': 'https://database.example.com/testdatabaseuri',
            'notes': 'Nothing to speak of',
            'blog_post': '',
            'video_url': '',
        }
        # First, create it:
        m = self.post('api_2_databases_collection', user=self.admin_user, data=post)
        self.assertEqual(m.status_code, 201)

        # Next, delete it:
        urlargs = {'pk': m.json['id']}
        m = self.delete('api_2_databases_member', user=self.admin_user, urlargs=urlargs,
                        data=post)
        self.assertEqual(m.status_code, 204)

class DatabaseLookup(TestCase):
        def setUp(self):
                pass

        def test_select_country(self):
                """Select a country from the country list"""
                pass


