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

from projects.models import Project, Story, StoryVersion, StoryTranslation


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
    # self.helper_create_dummy_users()
        # self.helper_cleanup_projects()

        # client = APIClient()
        # client.force_authenticate(user=self.staff_user)
        # delete_response = client.delete(reverse('story_delete', kwargs={'id': story.id}))

        # self.assertEqual(delete_response.status_code, status.HTTP_200_OK)
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

    def helper_cleanup_projects(self):
        self.helper_cleanup_story_translations()
        self.helper_cleanup_story_versions()
        self.helper_cleanup_stories()
        Project.objects.all().delete()

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

    # -- HELPER FUNCTIONS
    #
    #

    def helper_create_dummy_users(self):
        self.staff_user = get_user_model().objects.get(email=self.staff_email)
        self.admin_user = get_user_model().objects.get(email=self.admin_email)
        self.volunteer_user = get_user_model().objects.get(email=self.volunteer_email)
        self.user_user = get_user_model().objects.get(email=self.user_email)

    def helper_all_users_in_list_by_id(self, users, ids):
        num_users = len(users)
        num_users_found = 0

        if len(ids) != len(users):
            return False

        for user in users:
            for i in ids:
                if user.id == i:
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

    def test_create_translation(self):
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
