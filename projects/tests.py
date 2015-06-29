import datetime

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

from projects.models import Project, Story, StoryVersion, StoryTranslation, ProjectPlan


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

    dummy_reporters = None
    dummy_researchers = None
    dummy_editors = None
    dummy_copy_editors = None
    dummy_fact_checkers = None
    dummy_translators = None
    dummy_artists = None
    dummy_version_author = None
    dummy_project_plan_users = None

    # -- PROJECT TESTS
    #
    #

    # PROJECT COLLECTION
    def test_create_project(self):
        self.helper_create_dummy_users()
        self.helper_cleanup_projects()

        data = {'title': 'my created project',
                'description': 'my project description',
                'coordinator': self.staff_user.id,
                'users': [self.volunteer_user.id, self.staff_user.id]
                }
        client = APIClient()
        client.force_authenticate(user=self.staff_user)
        create_response = client.post(reverse('project_list'), data, format='json')

        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)

        # assert results in reply are what we expected
        results = create_response.data
        self.assertEqual(results['title'], 'my created project')
        self.assertEqual(results['description'], 'my project description')
        self.assertEqual(self.helper_all_users_in_list_by_id([self.staff_user], [results['coordinator']]),
                         True)
        self.assertEqual(self.helper_all_users_in_list_by_id([self.staff_user, self.volunteer_user], results['users']),
                         True)

        # get the object from the database and test against reply
        try:
            project = Project.objects.get(id=results['id'])
        except Project.DoesNotExist:
            project = None

        self.assertIsInstance(project, Project)
        self.assertEqual(project.title, results['title'])
        self.assertEqual(project.description, results['description'])
        self.assertEqual(self.helper_all_users_in_list_by_id([project.coordinator], [results['coordinator']]),
                         True)
        self.assertEqual(self.helper_all_users_in_list_by_id(project.users.all(), results['users']),
                         True)

        # test again without a description
        data = {'title': 'my created project 2',
                'coordinator': self.staff_user.id,
                'users': [self.volunteer_user.id, self.staff_user.id]
                }
        client = APIClient()
        client.force_authenticate(user=self.staff_user)
        create_response = client.post(reverse('project_list'), data, format='json')

        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)

        results = create_response.data
        self.assertEqual(results['description'] == "" or results['description'] is None, True)

    def test_list_projects(self):
        self.helper_create_dummy_users()
        self.helper_cleanup_projects()

        project_1 = self.helper_create_single_project('democracy for all 1',
                                          self.staff_user,
                                          [self.staff_user])
        project_2 = self.helper_create_single_project('democracy for all 2',
                                          self.admin_user,
                                          [self.volunteer_user])
        project_3 = self.helper_create_single_project('democracy for all 3',
                                          self.staff_user,
                                          [self.staff_user, self.volunteer_user])

        client = APIClient()
        client.force_authenticate(user=self.staff_user)
        list_response = client.get(reverse('project_list'))

        self.assertEqual(list_response.status_code, status.HTTP_200_OK)

        results = list_response.data['results']
        self.assertIsInstance(results, list)
        self.assertEqual(len(results), 3)

        self.assertEqual(results[0]['id'], project_1.id)
        self.assertEqual(results[0]['title'], 'democracy for all 1')
        self.assertEqual(self.helper_all_users_in_list_by_id([self.staff_user], [results[0]['coordinator']]),
                         True)
        self.assertEqual(self.helper_all_users_in_list_by_id([self.staff_user], results[0]['users']),
                         True)

        self.assertEqual(results[1]['id'], project_2.id)
        self.assertEqual(results[1]['title'], 'democracy for all 2')
        self.assertEqual(self.helper_all_users_in_list_by_id([self.admin_user], [results[1]['coordinator']]),
                         True)
        self.assertEqual(self.helper_all_users_in_list_by_id([self.volunteer_user], results[1]['users']),
                         True)

        self.assertEqual(results[2]['id'], project_3.id)
        self.assertEqual(results[2]['title'], 'democracy for all 3')
        self.assertEqual(self.helper_all_users_in_list_by_id([self.staff_user], [results[2]['coordinator']]),
                         True)
        self.assertEqual(self.helper_all_users_in_list_by_id([self.staff_user, self.volunteer_user], results[2]['users']),
                         True)

    # PROJECT MEMBER
    def test_get_project(self):
        self.helper_create_dummy_users()
        self.helper_cleanup_projects()

        project = self.helper_create_single_project('get democracy for all',
                                                    self.staff_user,
                                                    [self.staff_user])

        client = APIClient()
        client.force_authenticate(user=self.staff_user)
        get_response = client.get(reverse('project_detail', kwargs={'pk': project.id}))

        self.assertEqual(get_response.status_code, status.HTTP_200_OK)

        self.assertEqual(get_response.data['id'], project.id)
        self.assertEqual(get_response.data['title'], project.title)
        self.assertEqual(self.helper_all_users_in_list_by_id([project.coordinator], [get_response.data['coordinator']]),
                         True)
        self.assertEqual(self.helper_all_users_in_list_by_id(project.users.all(), get_response.data['users']),
                         True)

    def test_delete_project(self):
        self.helper_create_dummy_users()
        self.helper_cleanup_projects()

        project = self.helper_create_single_project('delete democracy for all',
                                                    self.staff_user,
                                                    [self.staff_user])

        client = APIClient()
        client.force_authenticate(user=self.staff_user)
        delete_response = client.delete(reverse('project_detail', kwargs={'pk': project.id}))

        self.assertEqual(delete_response.status_code, status.HTTP_204_NO_CONTENT)

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
                                                    [self.staff_user])

        data = {'title': 'altered title',
                'coordinator': self.admin_user.id,
                'users': [self.volunteer_user.id, self.user_user.id, self.staff_user.id]}
        client = APIClient()
        client.force_authenticate(user=self.staff_user)
        alter_response = client.put(reverse('project_detail', kwargs={'pk': project.id}), data, format='json')

        self.assertEqual(alter_response.status_code, status.HTTP_200_OK)
        self.assertEqual(alter_response.data['id'], project.id)
        self.assertEqual(alter_response.data['title'], 'altered title')
        self.assertEqual(self.helper_all_users_in_list_by_id([self.admin_user], [alter_response.data['coordinator']]),
                         True)
        self.assertEqual(self.helper_all_users_in_list_by_id([self.volunteer_user, self.user_user, self.staff_user], alter_response.data['users']),
                         True)

        try:
            project = Project.objects.get(id=project.id)
        except Project.DoesNotExist:
            project = None

        self.assertIsInstance(project, Project)
        self.assertEqual(alter_response.data['title'], project.title)
        self.assertEqual(alter_response.data['title'], 'altered title')
        self.assertEqual(self.helper_all_users_in_list_by_id([project.coordinator], [alter_response.data['coordinator']]),
                         True)
        self.assertEqual(self.helper_all_users_in_list_by_id(project.users.all(), alter_response.data['users']),
                         True)

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

    # STORY COLLECTION
    def test_create_story(self):
        self.helper_create_dummy_users()
        self.helper_cleanup_projects()

        project = self.helper_create_single_project('story create project',
                                                    self.staff_user,
                                                    self.staff_user,
                                                    [self.staff_user])

        data = {'project_id': project.id,
                'reporters': [self.user_user],
                'researchers': [self.user_user],
                'editors': [self.volunteer_user],
                'copy_editors': [self.volunteer_user],
                'fact_checkers': [self.admin_user],
                'translators': [self.admin_user],
                'artists': [self.staff_user],
                'published': ''
                }
        client = APIClient()
        client.force_authenticate(user=self.staff_user)
        create_response = client.post(reverse('story_create'), data)

        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)

        try:
            story = Story.objects.get(id=create_response.data['id'])
        except Story.DoesNotExist:
            story = None

        self.assertEqual(story.id, create_response.data['id'])
        self.assertEqual(story.project.id, project.id)
        self.assertEqual(story.reporters.all(), [self.user_user])
        self.assertEqual(story.researchers.all(), [self.user_user])
        self.assertEqual(story.editors.all(), [self.volunteer_user])
        self.assertEqual(story.copy_editors.all(), [self.volunteer_user])
        self.assertEqual(story.fact_checkers.all(), [self.admin_user])
        self.assertEqual(story.translators.all(), [self.admin_user])
        self.assertIsInstance(story.datetime, datetime)

    def test_list_stories(self):
        self.helper_create_dummy_users()
        self.helper_cleanup_projects()

        project = self.helper_create_single_project('story list project',
                                                    self.staff_user,
                                                    self.staff_user,
                                                    [self.staff_user])
        self.helper_create_single_story_dummy_wrapper('list story 1', project)
        self.helper_create_single_story_dummy_wrapper('list story 2', project)
        self.helper_create_single_story_dummy_wrapper('list story 3', project)

        client = APIClient()
        client.force_authenticate(user=self.staff_user)
        list_response = client.get(reverse('story_list', kwargs={'id': project.id}))

        self.assertEqual(list_response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(list_response.data, list)
        self.assertEqual(len(list_response.data), 3)
        self.assertGreater(list_response.data[0]['id'], 0)

    # STORY MEMBER
        # self.helper_create_dummy_users()
        # self.helper_cleanup_projects()

        # client = APIClient()
        # client.force_authenticate(user=self.staff_user)
        # delete_response = client.delete(reverse('story_delete', kwargs={'id': story.id}))

        # self.assertEqual(delete_response.status_code, status.HTTP_200_OK)

    def test_get_story_details(self):
        self.helper_create_dummy_users()
        self.helper_cleanup_projects()

        project = self.helper_create_single_project('getting a story project with details',
                                                    self.staff_user,
                                                    self.staff_user,
                                                    [self.staff_user])
        story = self.helper_create_single_story_dummy_wrapper('story with details to get', project)
        self.helper_create_single_story_version_dummy_wrapper(story, 'version 1')
        self.helper_create_single_story_version_dummy_wrapper(story, 'version 2')
        self.helper_create_single_story_version_dummy_wrapper(story, 'version 3')

        client = APIClient()
        client.force_authenticate(user=self.staff_user)
        details_response = client.get(reverse('story_details', kwargs={'id': story.id}))

        self.assertEqual(details_response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(details_response.data['versions'], list)
        self.assertEqual(len(details_response.data['versions']), 3)
        # assertion below is to check that the most recent version is the first in the list returned
        self.assertEqual(details_response.data['versions'][0]['title'], 'version 3')
        self.assertEqual(story.title, 'story with details to get')
        self.assertEqual(self.helper_all_users_in_list_by_id(story.reporters.all(),
                                                             details_response.data['reporters']), True)
        self.assertEqual(self.helper_all_users_in_list_by_id(story.researchers.all(),
                                                             details_response.data['researchers']), True)
        self.assertEqual(self.helper_all_users_in_list_by_id(story.editors.all(),
                                                             details_response.data['editors']), True)
        self.assertEqual(self.helper_all_users_in_list_by_id(story.copy_editors.all(),
                                                             details_response.data['copy_editors']), True)
        self.assertEqual(self.helper_all_users_in_list_by_id(story.fact_checkers.all(),
                                                             details_response.data['fact_checkers']), True)
        self.assertEqual(self.helper_all_users_in_list_by_id(story.researchers.all(),
                                                             details_response.data['translators']), True)
        self.assertEqual(self.helper_all_users_in_list_by_id(story.researchers.all(),
                                                             details_response.data['artists']), True)
        self.assertEqual(details_response.data['published'], story.published)
        self.assertEqual(details_response.data['podaci_root'], story.podaci_root)

    def test_delete_story(self):
        self.helper_create_dummy_users()
        self.helper_cleanup_projects()

        project = self.helper_create_single_project('deleting a story project',
                                                    self.staff_user,
                                                    self.staff_user,
                                                    [self.staff_user])
        story = self.helper_create_single_story_dummy_wrapper('delete story', project)

        client = APIClient()
        client.force_authenticate(user=self.staff_user)
        delete_response = client.delete(reverse('story_delete', kwargs={'id': story.id}))

        self.assertEqual(delete_response.status_code, status.HTTP_200_OK)

        try:
            story = Story.objects.get(id=story.id)
        except Story.DoesNotExist:
            story = None

        self.assertEqual(story, None)

    def test_alter_story(self):
        self.helper_create_dummy_users()
        self.helper_cleanup_projects()

        project = self.helper_create_single_project('altering a story version',
                                                    self.staff_user,
                                                    self.staff_user,
                                                    [self.staff_user])
        story = self.helper_create_single_story_dummy_wrapper('story to be altered', project)

        data = {'title': 'my altered title',
                'reporters': [self.admin_user.id],
                'researchers': [self.admin_user.id],
                'editors': [self.admin_user.id],
                'copy_editors': [self.admin_user.id],
                'fact_checkers': [self.admin_user.id],
                'translators': [self.admin_user.id],
                'artists': [self.admin_user.id],
                'published': ''
                }
        client = APIClient()
        client.force_authenticate(user=self.staff_user)
        alter_response = client.put(reverse('story_alter', kwargs={'id': story.id}), data, format='json')

        self.assertEqual(alter_response.status_code, status.HTTP_200_OK)

        story = Story.objects.get(id=story.id)

        self.assertEqual(story.title, 'my altered title')
        self.assertEqual(story.reporters.all(), [self.admin_user])
        self.assertEqual(story.researchers.all(), [self.admin_user])
        self.assertEqual(story.editors.all(), [self.admin_user])
        self.assertEqual(story.copy_editors.all(), [self.admin_user])
        self.assertEqual(story.fact_checkers.all(), [self.admin_user])
        self.assertEqual(story.translators.all(), [self.admin_user])
        self.assertEqual(story.artists.all(), [self.admin_user])

    def test_get_story_version(self):
        self.helper_create_dummy_users()
        self.helper_cleanup_projects()

        project = self.helper_create_single_project('getting a story version',
                                                    self.staff_user,
                                                    self.staff_user,
                                                    [self.staff_user])
        story = self.helper_create_single_story_dummy_wrapper('story with a version to get', project)
        story_version = self.helper_create_single_story_version_dummy_wrapper(story, 'version to get')

        client = APIClient()
        client.force_authenticate(user=self.staff_user)
        get_response = client.get(reverse('story_version_get', kwargs={'id': story_version.id}))

        self.assertEqual(get_response.status_code, status.HTTP_200_OK)
        self.assertEqual(get_response.data['id'], story_version.id)
        self.assertEqual(get_response.data['story'], story.id)
        self.assertEqual(get_response.data['authored'], story_version.authored.id)
        self.assertEqual(get_response.data['title'], 'version to get')
        self.assertEqual(get_response.data['text'], story_version.text)

    def test_create_story_version(self):
        self.helper_create_dummy_users()
        self.helper_cleanup_projects()

        project = self.helper_create_single_project('adding a story version project',
                                                    self.staff_user,
                                                    self.staff_user,
                                                    [self.staff_user])
        story = self.helper_create_single_story_dummy_wrapper('story with a version to be added', project)

        data = {'story': story.id,
                'authored': self.staff_user.id,
                'title': 'my added version',
                'text': 'my added version text'
                }
        client = APIClient()
        client.force_authenticate(user=self.staff_user)
        create_response = client.post(reverse('story_version_create', kwargs={'id': story.id}), data, format='json')

        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)

        try:
            story_version = StoryVersion.objects.get(id=create_response.data['id'])
        except:
            story_version = None

        self.assertEqual(story_version, StoryVersion)
        self.assertEqual(story_version.story.id, data['story'])
        self.assertEqual(story_version.authored.id, data['authored'])
        self.assertEqual(story_version.title, data['title'])
        self.assertEqual(story_version.text, data['text'])

    def test_alter_story_version(self):
        self.helper_create_dummy_users()
        self.helper_cleanup_projects()

        project = self.helper_create_single_project('altering a story version project',
                                                    self.staff_user,
                                                    self.staff_user,
                                                    [self.staff_user])
        story = self.helper_create_single_story_dummy_wrapper('story with a version to be altered', project)
        story_version = self.helper_create_single_story_version_dummy_wrapper(story, 'version to be altered')

        data = {'story': story.id,
                'authored': self.volunteer_user.id,
                'title': 'my altered title',
                'text': 'my altered text'
                }
        client = APIClient()
        client.force_authenticate(user=self.staff_user)
        alter_response = client.put(reverse('story_version_alter', kwargs={'id': story_version.id}), data, format='json')

        self.assertEqual(alter_response.status_code, status.HTTP_200_OK)

        story_version = StoryVersion.objects.get(id=story_version.id)

        self.assertEqual(story_version.story.id, story.id)
        self.assertEqual(story_version.authored.id, data['authored'])
        self.assertEqual(story_version.title, data['title'])
        self.assertEqual(story_version.text, data['text'])

    def test_delete_story_version(self):
        self.helper_create_dummy_users()
        self.helper_cleanup_projects()

        project = self.helper_create_single_project('deleting a story version',
                                                    self.staff_user,
                                                    self.staff_user,
                                                    [self.staff_user])
        story = self.helper_create_single_story_dummy_wrapper('story with a version to delete', project)
        story_version = self.helper_create_single_story_version_dummy_wrapper(story, 'version to delete')

        client = APIClient()
        client.force_authenticate(user=self.staff_user)
        delete_response = client.delete(reverse('story_version_delete', kwargs={'id': story.id}))

        self.assertEqual(delete_response.status_code, status.HTTP_200_OK)

        try:
            story_version = StoryVersion.objects.get(id=story_version.id)
        except StoryVersion.DoesNotExist:
            story_version = None

        self.assertEqual(story_version, None)

    def test_get_translation_of_most_recent_story_version(self):
        self.helper_create_dummy_users()
        self.helper_cleanup_projects()

        project = self.helper_create_single_project('most recent version of a story with translation project',
                                                    self.staff_user,
                                                    self.staff_user,
                                                    [self.staff_user])
        story = self.helper_create_single_story_dummy_wrapper('story with a version to delete', project)
        story_version = self.helper_create_single_story_version_dummy_wrapper(story, 'not most recent')
        story_version = self.helper_create_single_story_version_dummy_wrapper(story, 'most recent')
        story_translation = self.helper_create_single_story_translation_dummy_wrapper(story_version, 'el', 'my greek version')

        client = APIClient()
        client.force_authenticate(user=self.staff_user)
        get_response = client.get(reverse('story_version_most_recent_with_translation', kwargs={'id': story.id, 'language_code': 'el'}))

        self.assertEqual(get_response.status_code, status.HTTP_200_OK)
        self.assertEqual(get_response.data['id'], story_translation.id)
        self.assertEqual(get_response.data['version'], story_version.id)
        self.assertEqual(get_response.data['language_code'], story_translation.language_code)
        self.assertEqual(get_response.data['translator'], story_translation.translator.id)
        self.assertEqual(get_response.data['verified'], story_translation.verified)
        self.assertEqual(get_response.data['live'], story_translation.live)
        self.assertEqual(get_response.data['title'], story_translation.title)
        self.assertEqual(get_response.data['text'], story_translation.text)

    # def test_add_file_to_story(self):
    #     self.helper_create_dummy_users()
    #     self.helper_cleanup_projects()

    #     project = self.helper_create_single_project('adding a file a story project',
    #                                                 self.staff_user,
    #                                                 self.staff_user,
    #                                                 [self.staff_user])
    #     story = self.helper_create_single_story_dummy_wrapper('story to have file added to', project)

    #     client = APIClient()
    #     client.force_authenticate(user=self.staff_user)
    #     delete_response = client.delete(reverse('story_delete', kwargs={'id': story.id}))
    #     self.assertEqual(delete_response.status_code, status.HTTP_200_OK)

    # -- STORY TRANSLATION TESTS
    #
    #

    # STORY TRANSLATION COLLECTION/MEMBER
    def test_get_translation(self):
        self.helper_create_dummy_users()
        self.helper_cleanup_projects()

        project = self.helper_create_single_project('getting a story translation project',
                                                    self.staff_user,
                                                    self.staff_user,
                                                    [self.staff_user])
        story = self.helper_create_single_story_dummy_wrapper('story with a version with a translation', project)
        story_version = self.helper_create_single_story_version_dummy_wrapper(story, 'version with a translation')
        story_translation = self.helper_create_single_story_translation_dummy_wrapper(story_version, 'el', 'my greek version')

        client = APIClient()
        client.force_authenticate(user=self.staff_user)
        get_response = client.get(reverse('version_translation_get', kwargs={'id': story_version.id, 'language_code': 'el'}))

        self.assertEqual(get_response.status_code, status.HTTP_200_OK)
        self.assertEqual(get_response.data['version'], story_translation.version.id)
        self.assertEqual(get_response.data['language_code'], story_translation.language_code)
        self.assertEqual(get_response.data['translator'], story_translation.translator.id)
        self.assertEqual(get_response.data['title'], story_translation.title)
        self.assertEqual(get_response.data['text'], story_translation.text)

    def test_create_translation(self):
        self.helper_create_dummy_users()
        self.helper_cleanup_projects()

        project = self.helper_create_single_project('creating a story translation project',
                                                    self.staff_user,
                                                    self.staff_user,
                                                    [self.staff_user])
        story = self.helper_create_single_story_dummy_wrapper('story with a version with a translation to be created', project)

        data = {'language_code': 'el',
                'translator': self.volunteer_user.id,
                'verified': 1,
                'live': 0,
                'title': 'my greek translation',
                'text': 'pou einai o anthropos?'}
        client = APIClient()
        client.force_authenticate(user=self.staff_user)
        create_response = client.post(reverse('version_translation_create', kwargs={'id': story.id}), data, format='json')

        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)

        try:
            translation = StoryTranslation.object.get(id=create_response.data['id'])
        except StoryTranslation.DoesNotExist:
            translation = None

        self.assertIsInstance(translation, StoryTranslation)
        self.assertEqual(translation.language_code, data['language_code'])
        self.assertEqual(translation.translator.id, data['translator'])
        self.assertEqual(translation.verified, data['verified'])
        self.assertEqual(translation.title, data['title'])
        self.assertEqual(translation.text, data['text'])

    def test_alter_translation(self):
        self.helper_create_dummy_users()
        self.helper_cleanup_projects()

        project = self.helper_create_single_project('altering a story translation project',
                                                    self.staff_user,
                                                    self.staff_user,
                                                    [self.staff_user])
        story = self.helper_create_single_story_dummy_wrapper('story with a version with a translation to be altered', project)
        story_version = self.helper_create_single_story_version_dummy_wrapper(story, 'version with a translation to be altered')
        story_translation = self.helper_create_single_story_translation_dummy_wrapper(story_version, 'el', 'my greek version')

        data = {'language_code': 'ru',
                'translator': self.staff_user.id,
                'verified': 0,
                'live': 0,
                'title': 'my great russian title',
                'text': 'my great russian text'}
        client = APIClient()
        client.force_authenticate(user=self.staff_user)
        alter_response = client.put(reverse('version_translation_alter', kwargs={'id': story_translation.id}), data, format='json')

        self.assertEqual(alter_response.status_code, status.HTTP_200_OK)

        try:
            modified_translation = StoryTranslation.objects.get(id=alter_response.data['id'])
        except StoryTranslation.DoesNotExist:
            modified_translation = None

        self.assertIsInstance(modified_translation, StoryTranslation)
        self.assertEqual(modified_translation.id, story_translation.id)
        self.assertEqual(modified_translation.language_code, data['language_code'])
        self.assertEqual(modified_translation.translator.id, data['translator'])
        self.assertEqual(modified_translation.verified, data['verified'])
        self.assertEqual(modified_translation.title, data['title'])
        self.assertEqual(modified_translation.text, data['text'])

    def test_delete_translation(self):
        self.helper_create_dummy_users()
        self.helper_cleanup_projects()

        project = self.helper_create_single_project('altering a story translation project',
                                                    self.staff_user,
                                                    self.staff_user,
                                                    [self.staff_user])
        story = self.helper_create_single_story_dummy_wrapper('story with a version with a translation to be deleted', project)
        story_version = self.helper_create_single_story_version_dummy_wrapper(story, 'version with a translation to be deleted')
        story_translation = self.helper_create_single_story_translation_dummy_wrapper(story_version, 'el', 'my greek version')

        client = APIClient()
        client.force_authenticate(user=self.staff_user)
        delete_response = client.delete(reverse('version_translation_delete', kwargs={'id': story_translation.id}))

        self.assertEqual(delete_response.status_code, status.HTTP_200_OK)

        try:
            story_translation = StoryTranslation.objects.get(id=story_translation.id)
        except StoryTranslation.DoesNotExist:
            story_translation = None

        self.assertEqual(story_translation, None)

    # -- PROJECT PLAN TESTS
    #
    #

    # PROJECT PLAN COLLECTION
    def test_create_project_plan(self):
        self.helper_create_dummy_users()
        self.helper_cleanup_projects()

        project = self.helper_create_single_project('creating a project plan project',
                                                    self.staff_user,
                                                    self.staff_user,
                                                    [self.staff_user])
        story_1 = self.helper_create_single_story_dummy_wrapper('story for a project plan 1', project)
        story_2 = self.helper_create_single_story_dummy_wrapper('story for a project plan 2', project)

        data = {'start_date': datetime.datetime.now(),
                'end_date': datetime.datetime.now(),
                'title': 'my api project plan',
                'description': 'my api project plan description',
                'responsible_users': [self.volunteer_user.id, self.user_user.id],
                'related_stories': [story_1.id, story_2.id],
                'order': 1}
        client = APIClient()
        client.force_authenticate(user=self.staff_user)
        create_response = client.post(reverse('project_plan_create', kwargs={'id': project.id}), data, format='json')

        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)

        try:
            project_plan = ProjectPlan.objects.get(id=create_response.data['id'])
        except ProjectPlan.DoesNotExist:
            project_plan = None

        self.assertIsInstance(project_plan, ProjectPlan)
        self.assertEqual(project_plan.start_date, data['start_date'])
        self.assertEqual(project_plan.end_date, data['end_date'])
        self.assertEqual(project_plan.title, data['title'])
        self.assertEqual(project_plan.description, data['description'])
        self.assertEqual(self.helper_all_users_in_list_by_id(project_plan.responsible_users, data['responsible_users']), True)
        self.assertEqual(self.helper_all_users_in_list_by_id(project_plan.related_stories, data['responsible_users']), True)
        self.assertEqual(project_plan.order, data['order'])

    def test_list_project_plans(self):
        self.helper_create_dummy_users()
        self.helper_cleanup_projects()

        project = self.helper_create_single_project('listing project plans project',
                                                    self.staff_user,
                                                    self.staff_user,
                                                    [self.staff_user])
        story = self.helper_create_single_story_dummy_wrapper('story for a project plan list', project)
        project_plan = self.helper_create_single_project_plan_dummer_wrapper(project=project,
                                                                             title='my project plan 1',
                                                                             related_stories=[story],
                                                                             order=1)
        project_plan = self.helper_create_single_project_plan_dummer_wrapper(project=project,
                                                                             title='my project plan 2',
                                                                             related_stories=[story],
                                                                             order=2)

        client = APIClient()
        client.force_authenticate(user=self.staff_user)
        list_response = client.get(reverse('project_plan_list', kwargs={'id': story.id}))

        self.assertEqual(list_response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(list_response.data, list)
        self.assertEqual(len(list_response.data), 2)
        self.assertEqual(list_response.data[0]['id'], 1)

    #PROJECT PLAN MEMBERS
    def helper_get_project_plan(self):
        self.helper_create_dummy_users()
        self.helper_cleanup_projects()

        project = self.helper_create_single_project('getting a project plan project',
                                                    self.staff_user,
                                                    self.staff_user,
                                                    [self.staff_user])
        story = self.helper_create_single_story_dummy_wrapper('story for a project plan get', project)
        project_plan = self.helper_create_single_project_plan_dummer_wrapper(project=project,
                                                                             title='my project plan',
                                                                             related_stories=[story],
                                                                             order=1)

        client = APIClient()
        client.force_authenticate(user=self.staff_user)
        get_response = client.get(reverse('project_plan_get', kwargs={'id': project_plan.id}))

        self.assertEqual(get_response.status_code, status.HTTP_200_OK)
        self.assertEqual(project_plan.id, get_response.data['id'])
        self.assertEqual(project_plan.start_date, get_response.data['start_date'])
        self.assertEqual(project_plan.end_date, get_response.data['end_date'])
        self.assertEqual(project_plan.title, get_response.data['title'])
        self.assertEqual(project_plan.description, get_response.data['description'])
        self.assertEqual(self.helper_all_users_in_list_by_id(project_plan.responsible_users, data['responsible_users']), True)
        self.assertEqual(self.helper_all_users_in_list_by_id(project_plan.related_stories, data['related_stories']), True)
        self.assertEqual(project_plan.order, get_response.data['order'])

    def helper_alter_project_plan(self):
        self.helper_create_dummy_users()
        self.helper_cleanup_projects()

        project = self.helper_create_single_project('altering a project plan project',
                                                    self.staff_user,
                                                    self.staff_user,
                                                    [self.staff_user])
        story = self.helper_create_single_story_dummy_wrapper('story for a project plan alter', project)
        project_plan = self.helper_create_single_project_plan_dummer_wrapper(project=project,
                                                                             title='my project plan',
                                                                             related_stories=[story],
                                                                             order=1)
        story_1 = self.helper_create_single_story_dummy_wrapper('story for a project plan 1', project)

        data = {'start_date': datetime.datetime.now() + datetime.timedelta(10),
                'end_date': datetime.datetime.now() + datetime.timedelta(10),
                'title': 'my altered title',
                'description': 'my altered description',
                'responsible_users': [self.volunteer_user.id, self.user_user.id],
                'related_stories': [story_1.id],
                'order': 5}
        client = APIClient()
        client.force_authenticate(user=self.staff_user)
        alter_response = client.put(reverse('project_plan_alter', kwargs={'id': project_plan.id}))

        self.assertEqual(alter_response.status_code, status.HTTP_200_OK)

        project_plan = ProjectPlan.objects.get(id=project_plan.id)

        self.assertIsInstance(project_plan, ProjectPlan)
        self.assertEqual(project_plan.start_date, data['start_date'])
        self.assertEqual(project_plan.end_date, data['end_date'])
        self.assertEqual(project_plan.title, data['title'])
        self.assertEqual(project_plan.description, data['description'])
        self.assertEqual(self.helper_all_users_in_list_by_id(project_plan.responsible_users, data['responsible_users']), True)
        self.assertEqual(self.helper_all_users_in_list_by_id(project_plan.related_stories, data['responsible_users']), True)
        self.assertEqual(project_plan.order, data['order'])

    def helper_delete_project_plan(self):
        self.helper_create_dummy_users()
        self.helper_cleanup_projects()

        project = self.helper_create_single_project('deleting a project plan project',
                                                    self.staff_user,
                                                    self.staff_user,
                                                    [self.staff_user])
        story = self.helper_create_single_story_dummy_wrapper('story for a project plan delete', project)
        project_plan = self.helper_create_single_project_plan_dummer_wrapper(project=project,
                                                                             title='my project plan',
                                                                             related_stories=[story],
                                                                             order=1)

        client = APIClient()
        client.force_authenticate(user=self.staff_user)
        delete_response = client.delete(reverse('project_plan_delete', kwargs={'id': story.id}))

        self.assertEqual(delete_response.status_code, status.HTTP_200_OK)

        try:
            project_plan = ProjectPlan.objects.get(id=project_plan.id)
        except ProjectPlan.DoesNotExist:
            project_plan = None

        self.assertEqual(project_plan, None)

    # -- PROJECT HELPER FUNCTIONS
    #
    #
    def helper_create_single_project(self, project_title, coordinator, users):
        project = Project(title=project_title,
                          coordinator=coordinator)
        project.save()
        project.users.add(*users)
        project.save()

        return project

    def helper_cleanup_projects(self):
        self.helper_cleanup_story_translations()
        self.helper_cleanup_story_versions()
        self.helper_cleanup_stories()
        self.helper_cleanup_project_plans()
        Project.objects.all().delete()

    # -- PROJECT PLAN HELPER FUNCTIONS
    #
    #
    def helper_create_single_project_plan(self, project, start_date, end_date, title, description, responsible_users, related_stories, order):
        plan = ProjectPlan(project=project,
                           start_date=start_date,
                           end_date=end_date,
                           title=title,
                           description=description,
                           order=order)
        plan.save()
        plan.responsible_users.add(*responsible_users)
        plan.related_stories.add(*related_stories)
        plan.save()

        return plan

    def helper_create_single_project_plan_dummer_wrapper(self, project, title, related_stories, order):
        self.helper_set_story_dummy_participants()
        return self.helper_create_single_project_plan(project=project,
                                                      start_date=datetime.datetime.now(),
                                                      end_date=datetime.datetime.now() + datetime.timedelta(7),
                                                      title=title,
                                                      description='dummy project plan description',
                                                      responsible_users=self.dummy_project_plan_users,
                                                      related_stories=related_stories,
                                                      order=order)

    def helper_cleanup_project_plans(self):
        ProjectPlan.objects.all().delete()

    # -- STORY HELPER FUNCTIONS
    #
    #
    def helper_create_single_story(self, project, title, reporters, researchers, editors, copy_editors, fact_checkers, translators, artists):
        story = Story(project=project, title=title, published=datetime.datetime.now())
        story.save()
        story.reporters.add(*reporters)
        story.researchers.add(*researchers)
        story.editors.add(*editors)
        story.copy_editors.add(*copy_editors)
        story.fact_checkers.add(*fact_checkers)
        story.translators.add(*translators)
        story.artists.add(*artists)
        story.save()

        return story

    def helper_create_single_story_dummy_wrapper(self, title, project):
        self.helper_set_story_dummy_participants()
        return self.helper_create_single_story(title=title,
                                               project=project,
                                               reporters=self.dummy_reporters,
                                               researchers=self.dummy_researchers,
                                               editors=self.dummy_editors,
                                               copy_editors=self.dummy_copy_editors,
                                               fact_checkers=self.dummy_fact_checkers,
                                               translators=self.dummy_fact_checkers,
                                               artists=self.dummy_artists)

    def helper_create_single_story_version(self, story, timestamp, author, title, text):
        story_version = StoryVersion(story=story,
                                     timestamp=timestamp,
                                     authored=author,
                                     title=title,
                                     text=text)
        story_version.save()

        return story_version

    def helper_create_single_story_version_dummy_wrapper(self, story, title):
        self.helper_set_story_dummy_participants()
        return self.helper_create_single_story_version(story=story,
                                                       timestamp=datetime.datetime.now(),
                                                       author=self.dummy_version_author,
                                                       title=title,
                                                       text='im a dummy story version')

    def helper_create_single_story_translation(self, version, language_code, translator, verified, live, title, text):
        translation = StoryTranslation(version=version,
                                       language_code=language_code,
                                       translator=translator,
                                       verified=verified,
                                       live=live,
                                       title=title,
                                       text=text)
        translation.save()
        return translation

    def helper_create_single_story_translation_dummy_wrapper(self, version, language_code, title):
        self.helper_set_story_dummy_participants()
        return self.helper_create_single_story_translation(version=version,
                                                           language_code=language_code,
                                                           translator=self.volunteer_user,
                                                           verified=True,
                                                           live=True,
                                                           title=title,
                                                           text='im a translation! hear me roar!')

    def helper_cleanup_stories(self):
        Story.objects.all().delete()

    def helper_cleanup_story_versions(self):
        StoryVersion.objects.all().delete()

    def helper_cleanup_story_translations(self):
        StoryTranslation.objects.all().delete()

    def helper_set_story_dummy_participants(self):
        self.dummy_reporters = [self.user_user]
        self.dummy_researchers = [self.user_user]
        self.dummy_editors = [self.volunteer_user]
        self.dummy_copy_editors = [self.volunteer_user]
        self.dummy_fact_checkers = [self.admin_user]
        self.dummy_translators = [self.admin_user]
        self.dummy_artists = [self.staff_user]
        self.dummy_version_author = self.volunteer_user
        self.dummy_project_plan_users = [self.user_user, self.volunteer_user]

    # -- HELPER FUNCTIONS
    #
    #

    def helper_create_dummy_users(self):
        self.staff_user = get_user_model().objects.get(email=self.staff_email)
        self.admin_user = get_user_model().objects.get(email=self.admin_email)
        self.volunteer_user = get_user_model().objects.get(email=self.volunteer_email)
        self.user_user = get_user_model().objects.get(email=self.user_email)

    def helper_all_users_in_list_by_id(self, users, ids):
        """
        users is a list of django user objects
        ids assumes a multidimensional list/dict
        """

        num_users = len(users)
        num_users_found = 0

        if len(ids) != len(users):
            return False

        for user in users:
            for i in ids:
                if user.id == i['id']:
                    num_users_found += 1
                    break

        if num_users == num_users_found:
            return True

        return False

    #
    #

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

    def test_add_art(self):
        pass

    def test_add_documents(self):
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
