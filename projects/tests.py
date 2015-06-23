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

from projects.models import Project


class PipelineAPITest(APITestCase):
    fixtures = ['id/fixtures/initial_data.json']

    staff_email = 'staff@example.com'
    admin_email = 'admin@example.com'
    volunteer_email = 'volunteer@example.com'
    user_email = 'user@example.com'

    staff_user = None
    admin_user = None
    volunteer_user = None
    user_user = None

    # -- PROJECT TESTS
    #
    #

    # COLLECTION
    def test_create_project(self):
        user = get_user_model().objects.get(email=self.staff_email)
        title = 'democracy for all'
        coordinator_id = user.id
        users = [user.id]
        response = self.helper_create_single_project('create democracy for all',
                                                     user,
                                                     coordinator_id,
                                                     users)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data.title, title)
        self.assertEqual(response.data.coordinator.id, coordinator_id)
        self.assertEqual(response.data.users, users)

        helper_cleanup_projects()
        return

    def test_list_projects(self):
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

        helper_cleanup_projects()
        return

    # MEMBER
    def test_get_project(self):
        user = get_user_model().objects.get(email=self.staff_email)
        response = self.helper_create_single_project('get democracy for all',
                                                     user,
                                                     user.id,
                                                     [user.id])

        client = APIClient()
        client.force_authenticate(user=user)
        response = client.get(reverse('project_get', kwargs={'id': response.data.id}))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.id, response.id)

        helper_cleanup_projects()
        return

    def test_delete_project(self):
        user = get_user_model().objects.get(email=self.staff_email)
        create_response = self.helper_create_single_project('delete democracy for all',
                                                            user,
                                                            user.id,
                                                            [user.id])

        client = APIClient()
        client.force_authenticate(user=user)
        response = client.delete(reverse('project_delete', kwargs={'id': create_response.data.id}))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.id, create_response.data.id)

        response = client.get(reverse('project_get', kwargs={'id': create_response.data.id}))

        self.assertEqual(response.status_code, status_code.HTTP_404_NOT_FOUND)

        helper_cleanup_projects()
        return

    def test_alter_project(self):
        user = get_user_model().objects.get(email=self.staff_email)
        create_response = self.helper_create_single_project('alter democracy for all',
                                                            user,
                                                            user.id,
                                                            [user.id])

        altered_title = 'altered title via test'
        altered_user = get_user_model().objects.get(email=self.admin_email)
        data = {'title': altered_title,
                'coordinator': altered_user.id}
        client = APIClient()
        client.force_authenticate(user=user)
        alter_response = client.put(reverse('project_alter', kwargs={'id': create_response.data.id}), data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.title, altered_title)
        self.assertEqual(response.data.coordinator, altered_user.id)

        helper_cleanup_projects()
        return

    def test_assign_project_users(self):
        self.helper_create_dummy_users()
        create_response = self.helper_create_single_project('alter democracy for all',
                                                            staff_user,
                                                            user.id,
                                                            [user.id])

        data = {'users': [admin_user.id, volunteer_user.id, user_user.id]}
        client = APIClient()
        client.force_authenticate(user=creating_user)
        response = client.post(reverse('project_add_users', kwargs={'id': create_response.data.id}), data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)

        helper_cleanup_projects()
        return

    # -- PROJECT STORY TESTS
    #
    #

    def test_create_story(self):
        return

    # -- PROJECT HELPER FUNCTIONS
    #
    #
    def helper_create_single_project(self, project_title, creating_user, coordinator, users):
        url = reverse('project_create')
        client = APIClient()
        client.force_authenticate(user=creating_user)

        data = {'title': project_title,
                'coordinator': coordinator,
                'users': users}

        return client.post(url, data, format='json')

    def helper_create_single_story(self, project, reporters, researchers, editors, copy_editors, fact_checkers, translators, artists):
        pass

    def helper_cleanup_projects():
        Project.objects.all().delete()

        return

    # -- HELPER FUNCTIONS
    #
    #
    def helper_create_dummy_users():
        staff_user = get_user_model().objects.get(email=self.staff_email)
        admin_email = get_user_model().objects.get(email=self.admin_email)
        volunteer_user = get_user_model().objects.get(email=self.volunteer_email)
        user_user = get_user_model().objects.get(email=self.user_email)

        return
    #
    #

    def test_unassign_project_users(self):
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
