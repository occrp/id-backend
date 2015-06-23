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

    # PROJECT COLLECTION
    def test_create_project(self):
        self.helper_create_dummy_users()
        self.helper_cleanup_projects()

        create_response = self.helper_create_single_project_with_api('create democracy for all',
                                                                     self.staff_user,
                                                                     self.staff_user.id,
                                                                     [self.staff_user.id])

        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(create_response.data.title, title)
        self.assertEqual(create_response.data.coordinator.id, coordinator_id)
        self.assertEqual(create_response.data.users, users)

    def test_list_projects(self):
        self.helper_create_dummy_users()
        self.helper_cleanup_projects()

        self.helper_create_single_project('democracy for all 1',
                                          self.staff_user,
                                          self.staff_user.id,
                                          [self.staff_user.id])
        self.helper_create_single_project('democracy for all 2',
                                          self.staff_user,
                                          self.staff_user.id,
                                          [self.staff_user.id])
        self.helper_create_single_project('democracy for all 3',
                                          self.staff_user,
                                          self.staff_user.id,
                                          [self.staff_user.id])

        client = APIClient()
        client.force_authenticate(user=self.staff_user)
        list_response = client.get(reverse('project_list'))

        print list_response

        self.assertEqual(list_response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(list_response.data, list)
        self.assertEqual(len(list_response.data), 3)
        self.assertGreater(list_response.data[0]['id'], 0)

    # PROJECT MEMBER
    def test_get_project(self):
        self.helper_create_dummy_users()
        self.helper_cleanup_projects()

        project = self.helper_create_single_project('get democracy for all',
                                                    self.staff_user,
                                                    self.staff_user.id,
                                                    [self.staff_user.id])

        client = APIClient()
        client.force_authenticate(user=self.staff_user)
        get_response = client.get(reverse('project_get', kwargs={'id': project.id}))

        self.assertEqual(get_response.status_code, status.HTTP_200_OK)
        self.assertEqual(get_response.data['id'], project.id)

    def test_delete_project(self):
        self.helper_create_dummy_users()
        self.helper_cleanup_projects()

        project = self.helper_create_single_project('delete democracy for all',
                                                    self.staff_user,
                                                    self.staff_user.id,
                                                    [self.staff_user.id])

        client = APIClient()
        client.force_authenticate(user=self.staff_user)
        delete_response = client.delete(reverse('project_delete', kwargs={'id': project.id}))

        self.assertEqual(delete_response.status_code, status.HTTP_200_OK)
        self.assertEqual(delete_response.data['id'], project.id)

        try:
            project = Project.objects.get(id=project.id)
        except Project.DoesNotExist:
            project = None

        self.assertEqual(project, None)

    def test_alter_project(self):
        self.helper_create_dummy_users()
        self.helper_cleanup_projects()

        project = self.helper_create_single_project('alter democracy for all',
                                                    self.staff_user,
                                                    self.staff_user.id,
                                                    [self.staff_user.id])

        altered_title = 'altered title via test'
        data = {'title': altered_title,
                'coordinator': self.admin_user.id}
        client = APIClient()
        client.force_authenticate(user=self.staff_user)
        alter_response = client.put(reverse('project_alter', kwargs={'id': project.id}), data, format='json')

        self.assertEqual(alter_response.status_code, status.HTTP_200_OK)
        self.assertEqual(alter_response.data['title'], altered_title)
        self.assertEqual(alter_response.data['coordinator'], altered_user.id)

    # PROJECT USER COLLECTION
    def test_assign_project_users(self):
        self.helper_create_dummy_users()
        self.helper_cleanup_projects()

        project = self.helper_create_single_project('assign user democracy for all',
                                                    self.staff_user,
                                                    self.staff_user.id,
                                                    [self.staff_user.id])

        data = {'users': [self.admin_user.id, self.volunteer_user.id, self.user_user.id]}
        client = APIClient()
        client.force_authenticate(user=self.staff_user)
        assign_response = client.post(reverse('project_add_users', kwargs={'id': project.id}), data, format='json')
        project = Project.objects.get(id=project.id)

        self.assertEqual(assign_response.status_code, status.HTTP_200_OK)
        self.assertEqual(project.users.count(), 4)

    def test_unassign_project_users(self):
        self.helper_create_dummy_users()
        self.helper_cleanup_projects()

        project = self.helper_create_single_project('unassign user democracy for all',
                                                    self.staff_user,
                                                    self.staff_user,
                                                    [self.staff_user, self.admin_user, self.volunteer_user, self.user_user])

        data = {'users': [self.volunteer_user.id]}
        client = APIClient()
        client.force_authenticate(user=self.staff_user)
        unassign_response = client.delete(reverse('project_remove_users', kwargs={'id': project.id}), data, format='json')
        project = Project.objects.get(id=project.id)

        self.assertEqual(unassign_response.status_code, status.HTTP_200_OK)
        self.assertEqual(project.users.count(), 3)

    def test_list_project_users(self):
        self.helper_create_dummy_users()
        self.helper_cleanup_projects()

        project = self.helper_create_single_project('list user democracy for all',
                                                    self.staff_user,
                                                    self.staff_user,
                                                    [self.staff_user, self.admin_user, self.volunteer_user, self.user_user])

        client = APIClient()
        client.force_authenticate(user=self.staff_user)
        list_response = client.get(reverse('project_list_users', kwargs={'id': project.id}))

        self.assertEqual(list_response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(list_response.data['users']), 4)

    # -- PROJECT STORY TESTS
    #
    #

    def test_create_story(self):
        pass

    # -- PROJECT HELPER FUNCTIONS
    #
    #
    def helper_create_single_project(self, project_title, creating_user, coordinator, users):
        project = Project(title=project_title,
                          coordinator=creating_user)
        project.save()
        project.users.add(*users)
        project.save()

        return project

    def helper_create_single_project_with_api(self, project_title, creating_user, coordinator, users):
        url = reverse('project_create')
        client = APIClient()
        client.force_authenticate(user=creating_user)

        data = {'title': project_title,
                'coordinator': coordinator,
                'users': users}

        return client.post(url, data, format='json')

    def helper_create_single_story(self, project, reporters, researchers, editors, copy_editors, fact_checkers, translators, artists):
        pass

    def helper_cleanup_projects(self):
        Project.objects.all().delete()

    # -- HELPER FUNCTIONS
    #
    #
    def helper_create_dummy_users(self):
        self.staff_user = get_user_model().objects.get(email=self.staff_email)
        self.admin_user = get_user_model().objects.get(email=self.admin_email)
        self.volunteer_user = get_user_model().objects.get(email=self.volunteer_email)
        self.user_user = get_user_model().objects.get(email=self.user_email)

    #
    #

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
