from django.contrib.auth import get_user_model
from django.test import TestCase

from rest_framework.test import APIRequestFactory, APIClient, APITestCase
from rest_framework.reverse import reverse
from rest_framework import status

from core.tests import UserTestCase
#from core.tests import APITestCase
from core.testclient import TestClient
from core.testclient import APITestClient
from settings.settings import *


class PipelineAPITest(APITestCase):
    fixtures = ['id/fixtures/initial_data.json']
    staff_email = 'staff@example.com'

    # -- PROJECT LEVEL TESTS
    def test_project_create(self):
        user = get_user_model().objects.get(email=self.staff_email)
        response = self.helper_create_single_project('democracy for all',
                                                     user,
                                                     user.id,
                                                     [user.id])

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data, data)

    def test_get_project_list(self):
        user = get_user_model().objects.get(email=self.staff_email)

        self.helper_create_single_project('democracy for all 1',
                                          user,
                                          user.id,
                                          [user.id])
        self.helper_create_single_project('democracy for all 2',
                                          user,
                                          user.id,
                                          [user.id])
        self.helper_create_single_project('democracy for all 3',
                                          user,
                                          user.id,
                                          [user.id])

        client = APIClient()
        client.force_authenticate(user=user)
        response = client.get(reverse('project_list'))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)

        return

    # -- PROJECT HELPER FUNCTIONS
    def helper_create_single_project(self, project_title, creating_user, coordinator_id, user_ids):
        url = reverse('project_create')
        client = APIClient()
        client.force_authenticate(user=creating_user)

        data = {'title': project_title,
                'coordinator': coordinator_id,
                'users': user_ids}

        return client.post(url, data, format='json')

    def test_create_story(self):
        pass

    def test_delete_story(self):
        pass

    def test_assign_editor(self):
        pass

    def test_unassign_editor(self):
        pass

    def test_assign_journalist(self):
        pass

    def test_unassign_journalist(self):
        pass

    def test_assign_researcher(self):
        pass

    def test_unassign_researcher(self):
        pass

    def test_assign_copyeditor(self):
        pass

    def test_unassign_copyeditor(self):
        pass

    def test_assign_translator(self):
        pass

    def test_unassign_translator(self):
        pass

    def test_assign_artist(self):
        pass

    def test_unassign_artist(self):
        pass

    def test_set_story_status(self):
        pass

    def test_publish_story(self):
        pass

    def test_unpublish_story(self):
        pass

    def test_write_story(self):
        pass

    def test_alter_story(self):
        pass

    def test_add_art(self):
        pass

    def test_add_documents(self):
        pass

    def test_create_translation(self):
        pass

    def test_list_stories(self):
        pass

    def test_prioritize_stories(self):
        pass

    def test_add_comment(self):
        pass

    def test_edit_comment(self):
        pass

    def test_remove_comment(self):
        pass

    def test_lock_story(self):
        pass
