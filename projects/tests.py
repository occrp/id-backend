import datetime

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

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
    user2_email = 'user2@example.com'

    staff_user = None
    admin_user = None
    volunteer_user = None
    user_user = None
    user2_user = None

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

        client = APIClient()

        data = {'title': 'my created project',
                'description': 'my project description',
                'coordinators': [self.admin_user.id],
                'users': [self.volunteer_user.id, self.staff_user.id, self.admin_user.id]
                }
        client.force_authenticate(user=self.staff_user)
        create_response = client.post(reverse('project_list'), data, format='json')

        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)

        # assert results in reply are what we expected
        results = create_response.data
        self.assertEqual(results['title'], 'my created project')
        self.assertEqual(results['description'], 'my project description')

        self.assertEqual(self.helper_all_objects_in_list_by_id([self.staff_user, self.admin_user],
                                                               results['coordinators']),
                         True)
        self.assertEqual(self.helper_all_objects_in_list_by_id([self.staff_user, self.volunteer_user, self.admin_user],
                                                               results['users']),
                         True)

        # get the object from the database and test against call data
        try:
            project = Project.objects.get(id=results['id'])
        except Project.DoesNotExist:
            project = None

        self.assertIsInstance(project, Project)
        self.assertEqual(project.title, results['title'])
        self.assertEqual(project.description, results['description'])
        self.assertEqual(self.helper_all_objects_in_list_by_id(project.coordinators.all(),
                                                               [self.staff_user, self.admin_user]),
                         True)
        self.assertEqual(self.helper_all_objects_in_list_by_id(project.users.all(),
                                                               [self.staff_user, self.volunteer_user, self.admin_user]),
                         True)

        # test again without a description
        #
        data = {'title': 'my created project 2',
                'coordinators': [self.admin_user.id],
                'users': [self.volunteer_user.id, self.staff_user.id, self.admin_user.id]
                }
        client.force_authenticate(user=self.staff_user)
        create_response = client.post(reverse('project_list'), data, format='json')

        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)

        results = create_response.data
        self.assertEqual(results['title'], 'my created project 2')
        self.assertEqual(results['description'] == "" or results['description'] is None, True)

        self.assertEqual(self.helper_all_objects_in_list_by_id([self.staff_user, self.admin_user],
                                                               results['coordinators']),
                         True)
        self.assertEqual(self.helper_all_objects_in_list_by_id([self.staff_user, self.volunteer_user, self.admin_user],
                                                               results['users']),
                         True)

        # get the object from the database and test against call data
        try:
            project = Project.objects.get(id=results['id'])
        except Project.DoesNotExist:
            project = None

        self.assertIsInstance(project, Project)
        self.assertEqual(project.title, results['title'])
        self.assertEqual(project.description == "" or project.description is None, True)
        self.assertEqual(self.helper_all_objects_in_list_by_id(project.coordinators.all(),
                                                               [self.staff_user, self.admin_user]),
                         True)
        self.assertEqual(self.helper_all_objects_in_list_by_id(project.users.all(),
                                                               [self.staff_user, self.volunteer_user, self.admin_user]),
                         True)

        # test with coordinator as just an integer (as opposed to array of integers) and explicit coordinator as creator
        data = {'title': 'my created project 3',
                'description': 'my project description 3',
                'coordinators': self.staff_user.id,
                'users': [self.volunteer_user.id, self.staff_user.id, self.admin_user.id]
                }
        client.force_authenticate(user=self.staff_user)
        create_response = client.post(reverse('project_list'), data, format='json')

        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)

        # assert results in reply are what we expected
        results = create_response.data
        self.assertEqual(results['title'], 'my created project 3')
        self.assertEqual(results['description'], 'my project description 3')

        self.assertEqual(self.helper_all_objects_in_list_by_id([self.staff_user],
                                                               results['coordinators']),
                         True)
        self.assertEqual(self.helper_all_objects_in_list_by_id([self.staff_user, self.volunteer_user, self.admin_user],
                                                               results['users']),
                         True)

        # get the object from the database and test against call data
        try:
            project = Project.objects.get(id=results['id'])
        except Project.DoesNotExist:
            project = None

        self.assertIsInstance(project, Project)
        self.assertEqual(project.title, results['title'])
        self.assertEqual(project.description, results['description'])
        self.assertEqual(self.helper_all_objects_in_list_by_id(project.coordinators.all(),
                                                               [self.staff_user]),
                         True)
        self.assertEqual(self.helper_all_objects_in_list_by_id(project.users.all(),
                                                               [self.staff_user, self.volunteer_user, self.admin_user]),
                         True)

    def test_list_projects(self):
        self.helper_create_dummy_users()
        self.helper_cleanup_projects()

        project_1 = self.helper_create_single_project('democracy for all 1',
                                                      'description 1',
                                                      [self.staff_user],
                                                      [self.staff_user])
        project_2 = self.helper_create_single_project('democracy for all 2',
                                                      'description 2',
                                                      [self.volunteer_user],
                                                      [self.volunteer_user])
        project_3 = self.helper_create_single_project('democracy for all 3',
                                                      'description 3',
                                                      [self.staff_user],
                                                      [self.staff_user, self.volunteer_user])

        client = APIClient()
        client.force_authenticate(user=self.staff_user)
        list_response = client.get(reverse('project_list'))

        self.assertEqual(list_response.status_code, status.HTTP_200_OK)

        results = list_response.data['results']
        self.assertIsInstance(results, list)
        # we should only see two since one of which we created belongs to another user
        self.assertEqual(len(results), 2)

        self.assertEqual(results[0]['id'], project_1.id)
        self.assertEqual(results[0]['title'], 'democracy for all 1')
        self.assertEqual(results[0]['description'], 'description 1')
        self.assertEqual(self.helper_all_objects_in_list_by_id([self.staff_user],
                                                               results[0]['coordinators']),
                         True)
        self.assertEqual(self.helper_all_objects_in_list_by_id([self.staff_user],
                                                               results[0]['users']),
                         True)

        self.assertEqual(results[1]['id'], project_3.id)
        self.assertEqual(results[1]['title'], 'democracy for all 3')
        self.assertEqual(results[1]['description'], 'description 3')
        self.assertEqual(self.helper_all_objects_in_list_by_id([self.staff_user],
                                                               results[1]['coordinators']),
                         True)
        self.assertEqual(self.helper_all_objects_in_list_by_id([self.staff_user, self.volunteer_user],
                                                               results[1]['users']),
                         True)

        # test again with a list call for the volunteer user, should only see 2 results
        client = APIClient()
        client.force_authenticate(user=self.volunteer_user)
        list_response = client.get(reverse('project_list'))

        results = list_response.data['results']
        self.assertIsInstance(results, list)
        # we should only see two since one of which we created belongs to another user
        self.assertEqual(len(results), 2)

        self.assertEqual(results[0]['id'], project_2.id)
        self.assertEqual(results[0]['title'], 'democracy for all 2')
        self.assertEqual(results[0]['description'], 'description 2')
        self.assertEqual(self.helper_all_objects_in_list_by_id([self.volunteer_user],
                                                               results[0]['coordinators']),
                         True)
        self.assertEqual(self.helper_all_objects_in_list_by_id([self.volunteer_user],
                                                               results[0]['users']),
                         True)

        self.assertEqual(results[1]['id'], project_3.id)
        self.assertEqual(results[1]['title'], 'democracy for all 3')
        self.assertEqual(results[1]['description'], 'description 3')
        self.assertEqual(self.helper_all_objects_in_list_by_id([self.staff_user],
                                                               results[1]['coordinators']),
                         True)
        self.assertEqual(self.helper_all_objects_in_list_by_id([self.staff_user, self.volunteer_user],
                                                               results[1]['users']),
                         True)

    # PROJECT MEMBER
    def test_get_project(self):
        self.helper_create_dummy_users()
        self.helper_cleanup_projects()

        project = self.helper_create_single_project('get democracy for all',
                                                    'description 1 democracy',
                                                    [self.staff_user],
                                                    [self.staff_user])

        client = APIClient()
        client.force_authenticate(user=self.staff_user)
        get_response = client.get(reverse('project_detail', kwargs={'pk': project.id}))

        self.assertEqual(get_response.status_code, status.HTTP_200_OK)

        self.assertEqual(get_response.data['id'], project.id)
        self.assertEqual(get_response.data['title'], project.title)
        self.assertEqual(get_response.data['description'], project.description)
        self.assertEqual(self.helper_all_objects_in_list_by_id([self.staff_user],
                                                               get_response.data['coordinators']),
                         True)
        self.assertEqual(self.helper_all_objects_in_list_by_id([self.staff_user],
                                                               get_response.data['users']),
                         True)

        ## try get call again with different user, should be no results
        client = APIClient()
        client.force_authenticate(user=self.volunteer_user)
        get_response = client.get(reverse('project_detail', kwargs={'pk': project.id}))

        self.assertEqual(get_response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_project(self):
        self.helper_create_dummy_users()
        self.helper_cleanup_projects()

        project = self.helper_create_single_project('delete democracy for all',
                                                    'delete description',
                                                    [self.staff_user],
                                                    [self.staff_user, self.user_user])

        client = APIClient()
        client.force_authenticate(user=self.user_user)
        delete_response = client.delete(reverse('project_detail', kwargs={'pk': project.id}))

        # user_user should be able to see the project, but not alter or delete it
        self.assertEqual(delete_response.status_code, status.HTTP_403_FORBIDDEN)

        try:
            project = Project.objects.get(id=project.id)
        except Project.DoesNotExist:
            project = None

        self.assertIsInstance(project, Project)

        client = APIClient()
        client.force_authenticate(user=self.staff_user)
        delete_response = client.delete(reverse('project_detail', kwargs={'pk': project.id}))

        # try deletion again with user that had deletion rights
        self.assertEqual(delete_response.status_code, status.HTTP_204_NO_CONTENT)

        try:
            project = Project.objects.get(id=project.id)
        except Project.DoesNotExist:
            project = None

        self.assertEqual(project, None)

    def test_alter_project(self):
        self.helper_create_dummy_users()
        self.helper_cleanup_projects()

        project_title = 'title before alter'
        project_description = 'description before alter'
        project_coordinators = [self.staff_user]
        project_users = [self.staff_user, self.user_user]
        project = self.helper_create_single_project(project_title,
                                                    project_description,
                                                    project_coordinators,
                                                    project_users)
        project_id = project.id

        project_title_altered = 'altered title'
        project_description_altered = 'my altered description'
        project_coordinators_altered = [self.staff_user, self.admin_user]
        project_users_altered = [self.volunteer_user, self.user_user, self.staff_user]

        data = {'title': project_title_altered,
                'description': project_description_altered,
                'coordinators': [i.id for i in project_coordinators_altered],
                'users': [i.id for i in project_users_altered]}

        client = APIClient()
        client.force_authenticate(user=self.user_user)
        alter_response = client.put(reverse('project_detail', kwargs={'pk': project_id}), data, format='json')

        # user_user should not be able to alter the project
        self.assertEqual(alter_response.status_code, status.HTTP_403_FORBIDDEN)

        try:
            project = Project.objects.get(id=project_id)
        except Project.DoesNotExist:
            project = None

        self.assertIsInstance(project, Project)
        self.assertEqual(project.id, project_id)
        self.assertEqual(project.title, project_title)
        self.assertEqual(project.description, project_description)
        self.assertEqual(self.helper_all_objects_in_list_by_id(project.coordinators.all(),
                                                               project_coordinators),
                         True)
        self.assertEqual(self.helper_all_objects_in_list_by_id(project.users.all(),
                                                               project_users),
                         True)

        # try again with user with alter privelages
        client = APIClient()
        client.force_authenticate(user=self.staff_user)
        alter_response = client.put(reverse('project_detail', kwargs={'pk': project_id}), data, format='json')

        self.assertEqual(alter_response.status_code, status.HTTP_200_OK)

        try:
            project = Project.objects.get(id=alter_response.data['id'])
        except Project.DoesNotExist:
            project = None

        self.assertIsInstance(project, Project)

        self.assertEqual(alter_response.data['id'], project_id)
        self.assertEqual(alter_response.data['title'], project_title_altered)
        self.assertEqual(alter_response.data['description'], project_description_altered)
        self.assertEqual(self.helper_all_objects_in_list_by_id(project_coordinators_altered,
                                                               alter_response.data['coordinators']),
                         True)
        self.assertEqual(self.helper_all_objects_in_list_by_id(project_users_altered,
                                                               alter_response.data['users']),
                         True)

        self.assertEqual(project.id, project_id)
        self.assertEqual(project.title, project_title_altered)
        self.assertEqual(project.description, project_description_altered)
        self.assertEqual(self.helper_all_objects_in_list_by_id(project.coordinators.all(),
                                                               project_coordinators_altered),
                         True)
        self.assertEqual(self.helper_all_objects_in_list_by_id(project.users.all(),
                                                               project_users_altered),
                         True)

    # PROJECT USER COLLECTION
    def test_assign_project_users(self):
        self.helper_create_dummy_users()
        self.helper_cleanup_projects()

        project_users = [self.staff_user]
        project = self.helper_create_single_project('assign user democracy for all',
                                                    'assign description',
                                                    [self.staff_user],
                                                    project_users)

        project_users_to_add = [self.volunteer_user]
        project_users_altered = [self.staff_user, self.volunteer_user]
        data = {'users': [i.id for i in project_users_to_add]}

        client = APIClient()
        client.force_authenticate(user=self.user_user)
        assign_response = client.put(reverse('project_users', kwargs={'pk': project.id}), data, format='json')

        # since user is not in project, it should appear as if it doesn't exist
        self.assertEqual(assign_response.status_code, status.HTTP_404_NOT_FOUND)

        project = Project.objects.get(id=project.id)
        self.assertEqual(self.helper_all_objects_in_list_by_id(project.users.all(),
                                                               project_users),
                         True)

        client = APIClient()
        client.force_authenticate(user=self.staff_user)
        assign_response = client.put(reverse('project_users', kwargs={'pk': project.id}), data, format='json')

        project = Project.objects.get(id=project.id)
        self.assertEqual(self.helper_all_objects_in_list_by_id(project.users.all(),
                                                               project_users_altered),
                         True)

    def test_unassign_project_users(self):
        self.helper_create_dummy_users()
        self.helper_cleanup_projects()

        project_users = [self.staff_user, self.admin_user, self.user_user]
        project = self.helper_create_single_project('unassign user democracy for all',
                                                    'unassign description',
                                                    [self.staff_user],
                                                    project_users)

        project_users_to_remove = [self.user_user]
        project_users_altered = [self.staff_user, self.admin_user]
        data = {'users': [i.id for i in project_users_to_remove]}

        client = APIClient()
        client.force_authenticate(user=self.volunteer_user)
        unassign_response = client.delete(reverse('project_users', kwargs={'pk': project.id}), data, format='json')

        # since user is not in project, it should appear as if it doesn't exist
        self.assertEqual(unassign_response.status_code, status.HTTP_404_NOT_FOUND)

        project = Project.objects.get(id=project.id)
        self.assertEqual(self.helper_all_objects_in_list_by_id(project.users.all(),
                                                               project_users),
                         True)

        # try again with coordinator user
        client = APIClient()
        client.force_authenticate(user=self.staff_user)
        unassign_response = client.delete(reverse('project_users', kwargs={'pk': project.id}), data, format='json')

        self.assertEqual(unassign_response.status_code, status.HTTP_204_NO_CONTENT)

        project = Project.objects.get(id=project.id)
        self.assertEqual(self.helper_all_objects_in_list_by_id(project.users.all(),
                                                               project_users_altered),
                         True)

    def test_list_project_users(self):
        self.helper_create_dummy_users()
        self.helper_cleanup_projects()

        project = self.helper_create_single_project('list user democracy for all',
                                                    'list description',
                                                    [self.staff_user],
                                                    [self.staff_user, self.admin_user, self.volunteer_user])

        client = APIClient()
        client.force_authenticate(user=self.staff_user)
        list_response = client.get(reverse('project_users', kwargs={'pk': project.id}))

        self.assertEqual(list_response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(list_response.data['users']), 3)
        self.assertEqual(self.helper_all_objects_in_list_by_id([self.admin_user, self.admin_user, self.volunteer_user],
                                                               list_response.data['users']),
                         True)

        # try listing project users again with user not in the project, should get 404
        client = APIClient()
        client.force_authenticate(user=self.user_user)
        list_response = client.get(reverse('project_users', kwargs={'pk': project.id}))

        self.assertEqual(list_response.status_code, status.HTTP_404_NOT_FOUND)

    # -- PROJECT STORY TESTS
    #
    #

    # STORY COLLECTION
    def test_create_story(self):
        self.helper_create_dummy_users()
        self.helper_cleanup_projects()

        project = self.helper_create_single_project('story create project',
                                                    'story create description',
                                                    [self.staff_user],
                                                    [self.staff_user])

        data = {'project': project.id,
                'title': 'my story!',
                'thesis': 'my thesis!',
                'reporters': [self.user_user.id],
                'researchers': [self.user_user.id],
                'editors': [self.volunteer_user.id],
                'copy_editors': [self.volunteer_user.id],
                'fact_checkers': [self.admin_user.id],
                'translators': [self.admin_user.id],
                'artists': [self.staff_user.id],
                'published': None
                }

        client = APIClient()
        client.force_authenticate(user=self.user_user)
        create_response = client.post(reverse('story_list', kwargs={'pk': project.id}), data, format='json')

        # user_user should not be able to create a story since he isn't a coordinator
        self.assertEqual(create_response.status_code, status.HTTP_403_FORBIDDEN)

        # try call again with coordinator user
        client = APIClient()
        client.force_authenticate(user=self.staff_user)
        create_response = client.post(reverse('story_list', kwargs={'pk': project.id}), data, format='json')

        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)

        self.assertEqual(create_response.data['project'], project.id)
        self.assertEqual(create_response.data['title'], data['title'])
        self.assertEqual(create_response.data['thesis'], data['thesis'])
        self.assertEqual(self.helper_all_objects_in_list_by_id([self.user_user],
                                                               create_response.data['reporters']),
                         True)
        self.assertEqual(self.helper_all_objects_in_list_by_id([self.user_user],
                                                               create_response.data['researchers']),
                         True)
        self.assertEqual(self.helper_all_objects_in_list_by_id([self.volunteer_user],
                                                               create_response.data['editors']),
                         True)
        self.assertEqual(self.helper_all_objects_in_list_by_id([self.volunteer_user],
                                                               create_response.data['copy_editors']),
                         True)
        self.assertEqual(self.helper_all_objects_in_list_by_id([self.admin_user],
                                                               create_response.data['fact_checkers']),
                         True)
        self.assertEqual(self.helper_all_objects_in_list_by_id([self.admin_user],
                                                               create_response.data['translators']),
                         True)
        self.assertEqual(self.helper_all_objects_in_list_by_id([self.staff_user],
                                                               create_response.data['artists']),
                         True)

        try:
            story = Story.objects.get(id=create_response.data['id'])
        except Story.DoesNotExist:
            story = None

        self.assertEqual(story.project.id, project.id)
        self.assertEqual(story.title, create_response.data['title'])
        self.assertEqual(story.thesis, create_response.data['thesis'])

        self.assertEqual(self.helper_all_objects_in_list_by_id(story.reporters.all(),
                                                               [self.user_user]),
                         True)
        self.assertEqual(self.helper_all_objects_in_list_by_id(story.researchers.all(),
                                                               [self.user_user]),
                         True)
        self.assertEqual(self.helper_all_objects_in_list_by_id(story.editors.all(),
                                                               [self.volunteer_user]),
                         True)
        self.assertEqual(self.helper_all_objects_in_list_by_id(story.copy_editors.all(),
                                                               [self.volunteer_user]),
                         True)
        self.assertEqual(self.helper_all_objects_in_list_by_id(story.fact_checkers.all(),
                                                               [self.admin_user]),
                         True)
        self.assertEqual(self.helper_all_objects_in_list_by_id(story.translators.all(),
                                                               [self.admin_user]),
                         True)
        self.assertEqual(self.helper_all_objects_in_list_by_id(story.artists.all(),
                                                               [self.staff_user]),
                         True)

    def test_list_stories(self):
        self.helper_create_dummy_users()
        self.helper_cleanup_projects()

        project = self.helper_create_single_project('story list project',
                                                    'story lst project description',
                                                    [self.staff_user],
                                                    [self.staff_user])
        self.helper_create_single_story(project, 'list story 1', editors=[self.user_user])
        self.helper_create_single_story(project, 'list story 2', editors=[self.user_user])
        self.helper_create_single_story(project, 'list story 3')

        # staff_user should be able to see all 3
        client = APIClient()
        client.force_authenticate(user=self.staff_user)
        list_response = client.get(reverse('story_list', kwargs={'pk': project.id}))

        self.assertEqual(list_response.status_code, status.HTTP_200_OK)

        results = list_response.data['results']
        self.assertIsInstance(results, list)
        # only 2 because user_user should not be able to see story 3
        self.assertEqual(len(results), 3)
        self.assertEqual(results[0]['title'], 'list story 1')
        self.assertEqual(results[1]['title'], 'list story 2')
        self.assertEqual(results[2]['title'], 'list story 3')

        # user_user should only be able to see 2 since he is not a project member, but an editor on 2 of them
        client = APIClient()
        client.force_authenticate(user=self.user_user)
        list_response = client.get(reverse('story_list', kwargs={'pk': project.id}))

        self.assertEqual(list_response.status_code, status.HTTP_200_OK)

        results = list_response.data['results']
        self.assertIsInstance(results, list)
        # only 2 because user_user should not be able to see story 3
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]['title'], 'list story 1')
        self.assertEqual(results[1]['title'], 'list story 2')

    # STORY MEMBER
    def test_get_story_details(self):
        self.helper_create_dummy_users()
        self.helper_cleanup_projects()

        project = self.helper_create_single_project('getting a story project with details',
                                                    'gettiing a story project with details description',
                                                    [self.staff_user],
                                                    [self.staff_user])
        story = self.helper_create_single_story(project,
                                                'story with details to get',
                                                thesis='story with a thesis!',
                                                editors=[self.user_user],
                                                reporters=[self.user2_user])
        self.helper_create_single_story_version_dummy_wrapper(story, 'version 1')
        self.helper_create_single_story_version_dummy_wrapper(story, 'version 2')
        self.helper_create_single_story_version_dummy_wrapper(story, 'version 3')

        client = APIClient()
        client.force_authenticate(user=self.volunteer_user)
        details_response = client.get(reverse('story_detail', kwargs={'pk': story.id}))

        # volunteer_user should not be able to find the story. good for
        # security, as it doesn't provided unauthorized users knowledge of somethings
        # existances
        self.assertEqual(details_response.status_code, status.HTTP_404_NOT_FOUND)

        # staff_user (coordinator) should be able to get the story
        client = APIClient()
        client.force_authenticate(user=self.staff_user)
        details_response = client.get(reverse('story_detail', kwargs={'pk': story.id}))

        self.assertEqual(details_response.status_code, status.HTTP_200_OK)

        self.assertEqual(story.title, 'story with details to get')
        self.assertEqual(story.thesis, details_response.data['thesis'])
        self.assertEqual(self.helper_all_objects_in_list_by_id(story.reporters.all(),
                                                               details_response.data['reporters']),
                         True)
        self.assertEqual(self.helper_all_objects_in_list_by_id(story.researchers.all(),
                                                               details_response.data['researchers']),
                         True)
        self.assertEqual(self.helper_all_objects_in_list_by_id(story.editors.all(),
                                                               details_response.data['editors']),
                         True)
        self.assertEqual(self.helper_all_objects_in_list_by_id(story.copy_editors.all(),
                                                               details_response.data['copy_editors']),
                         True)
        self.assertEqual(self.helper_all_objects_in_list_by_id(story.fact_checkers.all(),
                                                               details_response.data['fact_checkers']),
                         True)
        self.assertEqual(self.helper_all_objects_in_list_by_id(story.translators.all(),
                                                               details_response.data['translators']),
                         True)
        self.assertEqual(self.helper_all_objects_in_list_by_id(story.artists.all(),
                                                               details_response.data['artists']),
                         True)
        self.assertGreater(1, self.helper_string_datetime_compare(details_response.data['published'], story.published))
        self.assertEqual(details_response.data['podaci_root'], story.podaci_root)
        self.assertEqual(details_response.data['version_count'], 3)

        verified_response = details_response.data.copy()

        # try again as user_user (story editor)
        client = APIClient()
        client.force_authenticate(user=self.user_user)
        details_response = client.get(reverse('story_detail', kwargs={'pk': story.id}))

        self.assertEqual(details_response.status_code, status.HTTP_200_OK)

        self.assertEqual(verified_response, details_response.data)

        # try again as user2_user (regular member/reporter)
        client = APIClient()
        client.force_authenticate(user=self.user2_user)
        details_response = client.get(reverse('story_detail', kwargs={'pk': story.id}))

        self.assertEqual(details_response.status_code, status.HTTP_200_OK)

        self.assertEqual(verified_response, details_response.data)

    def test_delete_story(self):
        self.helper_create_dummy_users()
        self.helper_cleanup_projects()

        project = self.helper_create_single_project(
            'deleting a story project',
            'delting a story project description',
            [self.staff_user],
            [self.staff_user]
        )
        story = self.helper_create_single_story(
            project,
            'delete story',
            editors=[self.staff_user],
            reporters=[self.user_user]
        )

        # try as as a reporter, this shouldn't work
        client = APIClient()
        client.force_authenticate(user=self.user_user)
        delete_response = client.delete(
            reverse('story_detail',
                    kwargs={'pk': story.id})
        )

        self.assertEqual(delete_response.status_code,
                         status.HTTP_403_FORBIDDEN)

        try:
            story = Story.objects.get(id=story.id)
        except Story.DoesNotExist:
            story = None

        self.assertIsInstance(story, Story)

        # try as a user that doesn't belong to the story, should not even be
        # able to see the story
        client = APIClient()
        client.force_authenticate(user=self.volunteer_user)
        delete_response = client.delete(
            reverse('story_detail',
                    kwargs={'pk': story.id})
        )

        self.assertEqual(delete_response.status_code,
                         status.HTTP_404_NOT_FOUND)

        try:
            story = Story.objects.get(id=story.id)
        except Story.DoesNotExist:
            story = None

        self.assertIsInstance(story, Story)

        # delete as editor, this should work
        client = APIClient()
        client.force_authenticate(user=self.staff_user)
        delete_response = client.delete(
            reverse('story_detail',
                    kwargs={'pk': story.id})
        )

        self.assertEqual(delete_response.status_code,
                         status.HTTP_204_NO_CONTENT)

        try:
            story = Story.objects.get(id=story.id)
        except Story.DoesNotExist:
            story = None

        self.assertEqual(story, None)

    def test_alter_story(self):
        self.helper_create_dummy_users()
        self.helper_cleanup_projects()

        project = self.helper_create_single_project(
            'altering a story project',
            'altering a story project description',
            [self.staff_user],
            [self.staff_user]
        )
        story = self.helper_create_single_story(
            project,
            'story to be altered',
            thesis='story to be altered thesis',
            editors=[self.staff_user, self.user_user],
            reporters=[self.volunteer_user]
        )
        # print story.published.isoformat()
        story_id = story.id

        story_reference = {'title': story.title,
                           'thesis': story.thesis,
                           'project': story.project,
                           'reporters': story.reporters.all(),
                           'researchers': story.researchers.all(),
                           'editors': story.editors.all(),
                           'copy_editors': story.copy_editors.all(),
                           'fact_checkers': story.fact_checkers.all(),
                           'translators': story.fact_checkers.all(),
                           'artists': story.artists.all(),
                           'published': story.published.isoformat(),
                           'podaci_root': story.podaci_root
                           }

        altered_date = timezone.now()
        data = {'title': 'my altered title',
                'thesis': 'my altered thesis',
                'project': story.project.id,
                'reporters': [self.admin_user.id],
                'researchers': [self.admin_user.id],
                'editors': [self.admin_user.id],
                'copy_editors': [self.admin_user.id],
                'fact_checkers': [self.admin_user.id],
                'translators': [self.admin_user.id],
                'artists': [self.admin_user.id],
                'published': altered_date.isoformat()
                }

        # try and modify as a user without that isn't on the projbect
        # user should not be able to see the project at all
        client = APIClient()
        client.force_authenticate(user=self.user2_user)
        alter_response = client.put(
            reverse('story_detail',
                    kwargs={'pk': story_id}),
            data,
            format='json'
        )

        self.assertEqual(alter_response.status_code, status.HTTP_404_NOT_FOUND)

        story = Story.objects.get(id=story_id)

        self.assertEqual(story.title, story_reference['title'])
        self.assertEqual(story.thesis, story_reference['thesis'])
        self.assertEqual(
            self.helper_all_objects_in_list_by_id(
                story.reporters.all(),
                story_reference['reporters']),
            True)
        self.assertEqual(
            self.helper_all_objects_in_list_by_id(
                story.researchers.all(),
                story_reference['researchers']),
            True)
        self.assertEqual(
            self.helper_all_objects_in_list_by_id(
                story.editors.all(),
                story_reference['editors']),
            True)
        self.assertEqual(
            self.helper_all_objects_in_list_by_id(
                story.copy_editors.all(),
                story_reference['copy_editors']),
            True)
        self.assertEqual(
            self.helper_all_objects_in_list_by_id(
                story.fact_checkers.all(),
                story_reference['fact_checkers']),
            True)
        self.assertEqual(
            self.helper_all_objects_in_list_by_id(
                story.translators.all(),
                story_reference['translators']),
            True)
        self.assertEqual(
            self.helper_all_objects_in_list_by_id(
                story.artists.all(),
                story_reference['artists']),
            True)
        self.assertEqual(
            story.published.isoformat(),
            story_reference['published']
        )
        self.assertEqual(story.podaci_root, story_reference['podaci_root'])

        # try and modify as a user without that doesn't have permissions
        client = APIClient()
        client.force_authenticate(user=self.volunteer_user)
        alter_response = client.put(
            reverse('story_detail',
                    kwargs={'pk': story_id}),
            data,
            format='json'
        )

        self.assertEqual(alter_response.status_code, status.HTTP_403_FORBIDDEN)

        story = Story.objects.get(id=story_id)

        self.assertEqual(story.title, story_reference['title'])
        self.assertEqual(story.thesis, story_reference['thesis'])
        self.assertEqual(
            self.helper_all_objects_in_list_by_id(
                story.reporters.all(),
                story_reference['reporters']),
            True)
        self.assertEqual(
            self.helper_all_objects_in_list_by_id(
                story.researchers.all(),
                story_reference['researchers']),
            True)
        self.assertEqual(
            self.helper_all_objects_in_list_by_id(
                story.editors.all(),
                story_reference['editors']),
            True)
        self.assertEqual(
            self.helper_all_objects_in_list_by_id(
                story.copy_editors.all(),
                story_reference['copy_editors']),
            True)
        self.assertEqual(
            self.helper_all_objects_in_list_by_id(
                story.fact_checkers.all(),
                story_reference['fact_checkers']),
            True)
        self.assertEqual(
            self.helper_all_objects_in_list_by_id(
                story.translators.all(),
                story_reference['translators']),
            True)
        self.assertEqual(
            self.helper_all_objects_in_list_by_id(
                story.artists.all(),
                story_reference['artists']),
            True)
        self.assertEqual(
            story.published.isoformat(),
            story_reference['published']
        )
        self.assertEqual(story.podaci_root, story_reference['podaci_root'])

        # this should work since staff_user is an editor
        client = APIClient()
        client.force_authenticate(user=self.staff_user)
        alter_response = client.put(
            reverse('story_detail',
                    kwargs={'pk': story_id}),
            data,
            format='json'
        )

        self.assertEqual(alter_response.status_code, status.HTTP_200_OK)

        story = Story.objects.get(id=story_id)
        result = alter_response.data

        self.assertEqual(result['id'], story_id)
        self.assertEqual(result['title'], story.title)
        self.assertEqual(result['thesis'], story.thesis)
        self.assertEqual(
            self.helper_all_objects_in_list_by_id(
                story.reporters.all(),
                result['reporters']),
            True)
        self.assertEqual(
            self.helper_all_objects_in_list_by_id(
                story.researchers.all(),
                result['researchers']),
            True)
        self.assertEqual(
            self.helper_all_objects_in_list_by_id(
                story.editors.all(),
                result['editors']),
            True)
        self.assertEqual(
            self.helper_all_objects_in_list_by_id(
                story.copy_editors.all(),
                result['copy_editors']),
            True)
        self.assertEqual(
            self.helper_all_objects_in_list_by_id(
                story.fact_checkers.all(),
                result['fact_checkers']),
            True)
        self.assertEqual(
            self.helper_all_objects_in_list_by_id(
                story.translators.all(),
                result['translators']),
            True)
        self.assertEqual(
            self.helper_all_objects_in_list_by_id(
                story.artists.all(),
                result['artists']),
            True)
        self.assertGreater(
            1,
            self.helper_string_datetime_compare(
                result['published'],
                story.published
            )
        )
        self.assertEqual(result['podaci_root'], story.podaci_root)

        self.assertEqual(story.title, data['title'])
        self.assertEqual(story.thesis, data['thesis'])
        self.assertEqual(
            self.helper_all_objects_in_list_by_id(
                story.reporters.all(),
                data['reporters']),
            True)
        self.assertEqual(
            self.helper_all_objects_in_list_by_id(
                story.researchers.all(),
                data['researchers']),
            True)
        self.assertEqual(
            self.helper_all_objects_in_list_by_id(
                story.editors.all(),
                data['editors']),
            True)
        self.assertEqual(
            self.helper_all_objects_in_list_by_id(
                story.copy_editors.all(),
                data['copy_editors']),
            True)
        self.assertEqual(
            self.helper_all_objects_in_list_by_id(
                story.fact_checkers.all(),
                data['fact_checkers']),
            True)
        self.assertEqual(
            self.helper_all_objects_in_list_by_id(
                story.translators.all(),
                data['translators']),
            True)
        self.assertEqual(
            self.helper_all_objects_in_list_by_id(
                story.artists.all(),
                data['artists']),
            True)
        self.assertGreater(
            1,
            self.helper_datetime_datetime_compare(
                altered_date,
                story.published
            )
        )
        self.assertEqual(story.podaci_root, story_reference['podaci_root'])

    # -- STORY VERSION TESTS
    #
    #

    # COLLECTION TESTS
    def test_create_story_version(self):
        self.helper_create_dummy_users()
        self.helper_cleanup_projects()

        project = self.helper_create_single_project(
            'adding a story version project',
            'adding a story version project description',
            [self.staff_user],
            [self.staff_user]
        )
        story = self.helper_create_single_story(
            project,
            'story with a version to be added',
            editors=[self.user_user],
            fact_checkers=[self.volunteer_user]
        )

        data = {'story': story.id,
                'title': 'my added version',
                'text': 'my added version text'
                }

        # try and create with volunteer_user, should not work since the user
        # is not project coordinator or story editor/copyeditor/reporter
        client = APIClient()
        client.force_authenticate(user=self.volunteer_user)
        create_response = client.post(
            reverse('story_version_list',
                    kwargs={'pk': story.id}),
            data,
            format='json'
        )

        self.assertEqual(create_response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(StoryVersion.objects.all().count(), 0)

        # try and create with user2_user, should not work since the user
        # is not project coordinator or story editor/copyeditor/reporter
        client = APIClient()
        client.force_authenticate(user=self.user2_user)
        create_response = client.post(
            reverse('story_version_list',
                    kwargs={'pk': story.id}),
            data,
            format='json'
        )

        self.assertEqual(create_response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(StoryVersion.objects.all().count(), 0)

        # try and create with staff_user, should work since user is a
        # coordinator
        client = APIClient()
        client.force_authenticate(user=self.staff_user)
        create_response = client.post(
            reverse('story_version_list',
                    kwargs={'pk': story.id}),
            data,
            format='json'
        )

        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(StoryVersion.objects.all().count(), 1)

        # try and create with user_user, should work since user is an
        # editor
        client = APIClient()
        client.force_authenticate(user=self.user_user)
        create_response = client.post(
            reverse('story_version_list',
                    kwargs={'pk': story.id}),
            data,
            format='json'
        )

        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(StoryVersion.objects.all().count(), 2)

        # just checking the last created story version, assuming that earlier
        # ones have worked based on object count

        try:
            story_version = StoryVersion.objects.get(id=create_response.data['id'])
        except:
            story_version = None

        self.assertIsInstance(story_version, StoryVersion)
        self.assertEqual(story_version.story.id, data['story'])
        self.assertEqual(story_version.author.id, self.user_user.id)
        self.assertEqual(story_version.title, data['title'])
        self.assertEqual(story_version.text, data['text'])

    def test_list_story_versions(self):
        self.helper_create_dummy_users()
        self.helper_cleanup_projects()

        project = self.helper_create_single_project(
            'listing a story version',
            'listing a story version description',
            [self.staff_user],
            [self.staff_user, self.user_user]
        )
        story = self.helper_create_single_story(
            project,
            'story with a versions to list',
            editors=[self.user_user],
            translators=[self.volunteer_user]
        )
        story_version = self.helper_create_single_story_version(
            story,
            title="version to list 1",
            author=self.user_user
        )
        story_version = self.helper_create_single_story_version(
            story,
            title="version to list 2",
            author=self.user_user
        )
        story_version = self.helper_create_single_story_version(
            story,
            title="version to list 3",
            author=self.user_user
        )

        # try to list as user2_user, should not be able to see anything
        client = APIClient()
        client.force_authenticate(user=self.user2_user)
        list_response = client.get(
            reverse('story_version_list',
                    kwargs={'pk': story.id}
                    )
        )

        self.assertEqual(list_response.status_code, status.HTTP_200_OK)

        results = list_response.data['results']
        self.assertIsInstance(results, list)
        self.assertEqual(len(results), 0)

        # try to list as volunteer_user, should be able to see 3
        client = APIClient()
        client.force_authenticate(user=self.volunteer_user)
        list_response = client.get(
            reverse('story_version_list',
                    kwargs={'pk': story.id}
                    )
        )

        self.assertEqual(list_response.status_code, status.HTTP_200_OK)

        results = list_response.data['results']
        self.assertIsInstance(results, list)
        self.assertEqual(len(results), 3)

        # try to list as staff_user, should be able to see 3
        client = APIClient()
        client.force_authenticate(user=self.staff_user)
        list_response = client.get(
            reverse('story_version_list',
                    kwargs={'pk': story.id}
                    )
        )

        self.assertEqual(list_response.status_code, status.HTTP_200_OK)

        results = list_response.data['results']
        self.assertIsInstance(results, list)
        self.assertEqual(len(results), 3)

        # test the titles, this should be good enough
        self.assertEqual(results[0]['title'], 'version to list 1')
        self.assertEqual(results[1]['title'], 'version to list 2')
        self.assertEqual(results[2]['title'], 'version to list 3')

    # MEMBER TESTS
    def test_get_story_version(self):
        self.helper_create_dummy_users()
        self.helper_cleanup_projects()

        project = self.helper_create_single_project(
            'getting a story version',
            'getting a story version description',
            [self.staff_user],
            [self.staff_user]
        )
        story = self.helper_create_single_story(
            project,
            'story with a version to get',
            editors=[self.volunteer_user],
            copy_editors=[self.user_user]
        )
        story_version = self.helper_create_single_story_version(
            story,
            title='version to get',
            author=self.volunteer_user
        )

        # try with user2_user, should not be able to see anything
        client = APIClient()
        client.force_authenticate(user=self.user2_user)
        get_response = client.get(
            reverse('story_version_detail',
                    kwargs={'pk': story_version.id}
                    )
        )

        self.assertEqual(get_response.status_code, status.HTTP_404_NOT_FOUND)

        # try with staff_user, should be able to see the story version
        client = APIClient()
        client.force_authenticate(user=self.staff_user)
        get_response = client.get(
            reverse('story_version_detail',
                    kwargs={'pk': story_version.id}
                    )
        )

        self.assertEqual(get_response.status_code, status.HTTP_200_OK)

        # try with volunteer_user, should be able to see the story version
        client = APIClient()
        client.force_authenticate(user=self.volunteer_user)
        get_response = client.get(
            reverse('story_version_detail',
                    kwargs={'pk': story_version.id}
                    )
        )

        self.assertEqual(get_response.status_code, status.HTTP_200_OK)

        self.assertEqual(get_response.data['id'], story_version.id)
        self.assertEqual(get_response.data['story'], story.id)
        self.assertEqual(get_response.data['author']['id'], story_version.author.id)
        self.assertEqual(get_response.data['title'], story_version.title)
        self.assertEqual(get_response.data['text'], story_version.text)

    def test_alter_story_version(self):
        self.helper_create_dummy_users()
        self.helper_cleanup_projects()

        project = self.helper_create_single_project(
            'altering a story version project',
            'altering a story version project description',
            [self.staff_user],
            [self.staff_user]
        )
        story = self.helper_create_single_story(
            project,
            'story with a version to be altered',
            editors=[self.user_user, self.staff_user],
            artists=[self.volunteer_user]
        )
        story_version = self.helper_create_single_story_version(
            story,
            title='version to be altered',
            author=self.user_user
        )
        # fixes the datetime comparison issue
        story_version = StoryVersion.objects.get(id=story_version.id)

        story_version_title = story_version.title
        story_version_text = story_version.text
        story_version_author = story_version.author
        story_version_timestamp = story_version.timestamp

        data = {'story': story.id,
                'author': self.staff_user.id,
                'title': 'my altered title',
                'text': 'my altered text',
                'timestamp': (datetime.datetime.now() + datetime.timedelta(3)).isoformat()
                }

        # try modification with volunteer_user, should receive a 403
        client = APIClient()
        client.force_authenticate(user=self.volunteer_user)
        alter_response = client.put(
            reverse('story_version_detail',
                    kwargs={'pk': story_version.id}
                    ),
            data,
            format='json'
        )

        self.assertEqual(alter_response.status_code, status.HTTP_403_FORBIDDEN)

        # try modification with volunteer_user, should receive a 404
        client = APIClient()
        client.force_authenticate(user=self.user2_user)
        alter_response = client.put(
            reverse('story_version_detail',
                    kwargs={'pk': story_version.id}
                    ),
            data,
            format='json'
        )

        self.assertEqual(alter_response.status_code, status.HTTP_404_NOT_FOUND)

        # test to make sure our story version hasn't modified
        story_version = StoryVersion.objects.get(id=story_version.id)
        self.assertEqual(story_version.author.id, story_version_author.id)
        self.assertEqual(story_version.title, story_version_title)
        self.assertEqual(story_version.text, story_version_text)
        self.assertEqual(story_version.timestamp.isoformat(),
                         story_version_timestamp.isoformat())

        # try modification as user_user
        client = APIClient()
        client.force_authenticate(user=self.user_user)
        alter_response = client.put(
            reverse('story_version_detail',
                    kwargs={'pk': story_version.id}
                    ),
            data,
            format='json'
        )

        self.assertEqual(alter_response.status_code, status.HTTP_200_OK)

        story_version = StoryVersion.objects.get(id=story_version.id)
        result = alter_response.data

        self.assertEqual(data['story'], result['story'])
        self.assertEqual(data['author'], result['author']['id'])
        self.assertEqual(data['title'], result['title'])
        self.assertEqual(data['text'], result['text'])

        self.assertEqual(story_version.story.id, story.id)
        self.assertEqual(story_version.author.id, result['author']['id'])
        self.assertEqual(story_version.title, result['title'])
        self.assertEqual(story_version.text, result['text'])
        self.assertGreater(1,
                           self.helper_string_datetime_compare(result['timestamp'],
                                                               story_version.timestamp
                                                               )
                           )

    def test_delete_story_version(self):
        self.helper_create_dummy_users()
        self.helper_cleanup_projects()

        project = self.helper_create_single_project(
            'deleting a story version',
            'deleting a story version description',
            [self.staff_user],
            [self.staff_user]
        )
        story = self.helper_create_single_story(
            project,
            'story with a version to delete',
            editors=[self.user_user],
            fact_checkers=[self.volunteer_user]
        )
        story_version = self.helper_create_single_story_version(
            story,
            title='version to delete',
            author=self.user_user
        )

        # try deleting with user2_user
        client = APIClient()
        client.force_authenticate(user=self.user2_user)
        delete_response = client.delete(
            reverse('story_version_detail',
                    kwargs={'pk': story_version.id}
                    )
        )

        self.assertEqual(delete_response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(StoryVersion.objects.all().count(), 1)

        # try deleting with volunteer_user
        client = APIClient()
        client.force_authenticate(user=self.volunteer_user)
        delete_response = client.delete(
            reverse('story_version_detail',
                    kwargs={'pk': story_version.id}
                    )
        )

        self.assertEqual(delete_response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(StoryVersion.objects.all().count(), 1)

        # try deleting with user2_user
        client = APIClient()
        client.force_authenticate(user=self.user_user)
        delete_response = client.delete(
            reverse('story_version_detail',
                    kwargs={'pk': story_version.id}
                    )
        )

        self.assertEqual(delete_response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(StoryVersion.objects.all().count(), 0)

    def test_get_translation_of_most_recent_story_version(self):
        self.helper_create_dummy_users()
        self.helper_cleanup_projects()

        project = self.helper_create_single_project(
            'most recent version of a story with translation project',
            'most recent version of a story with translation project description',
            [self.staff_user],
            [self.staff_user]
        )
        story = self.helper_create_single_story(
            project,
            'story with a version with a translation',
            editors=[self.staff_user]
        )
        story_version = self.helper_create_single_story_version(
            story,
            title='not most recent',
            author=self.staff_user
        )
        story_version = self.helper_create_single_story_version(
            story,
            title='most recent',
            author=self.staff_user
        )
        story_translation = self.helper_create_single_story_translation(
            story_version,
            language_code="el",
            text="my greek version",
            translator=self.volunteer_user,
            live=True
        )

        client = APIClient()
        client.force_authenticate(user=self.staff_user)
        get_response = client.get(
            reverse('story_live_version_in_language',
                    kwargs={'pk': story.id, 'language_code': 'el'}
                    )
        )

        self.assertEqual(get_response.status_code, status.HTTP_200_OK)
        self.assertEqual(get_response.data['id'], story_translation.id)
        self.assertEqual(get_response.data['version'], story_version.id)
        self.assertEqual(get_response.data['language_code'], story_translation.language_code)
        self.assertEqual(get_response.data['translator']['id'], story_translation.translator.id)
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

    # COLLECTION TESTS
    def test_create_translation(self):
        self.helper_create_dummy_users()
        self.helper_cleanup_projects()

        project = self.helper_create_single_project('creating a story translation project',
                                                    'creating a story translation project description',
                                                    [self.staff_user],
                                                    [self.staff_user])
        story = self.helper_create_single_story_dummy_wrapper('story with a version with a translation to be created', project)
        story_version = self.helper_create_single_story_version_dummy_wrapper(story, 'story version to get a translation')

        data = {'version': story_version.id,
                'language_code': 'el',
                'translator': self.volunteer_user.id,
                'verified': 1,
                'live': 0,
                'title': 'my greek translation',
                'text': 'pou einai o anthropos?'}
        client = APIClient()
        client.force_authenticate(user=self.staff_user)
        create_response = client.post(reverse('story_translation_list', kwargs={'pk': story_version.id}), data, format='json')

        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)

        try:
            translation = StoryTranslation.objects.get(id=create_response.data['id'])
        except StoryTranslation.DoesNotExist:
            translation = None

        self.assertIsInstance(translation, StoryTranslation)
        self.assertEqual(translation.version.id, story_version.id)
        self.assertEqual(translation.language_code, data['language_code'])
        self.assertEqual(translation.translator.id, data['translator'])
        self.assertEqual(translation.verified, data['verified'])
        self.assertEqual(translation.title, data['title'])
        self.assertEqual(translation.text, data['text'])

    def test_list_translations(self):
        self.helper_create_dummy_users()
        self.helper_cleanup_projects()

        project = self.helper_create_single_project('listing a story translation project',
                                                    'listing a story translation project description',
                                                    [self.staff_user],
                                                    [self.staff_user])
        story = self.helper_create_single_story_dummy_wrapper('story with a version with translations', project)
        story_version = self.helper_create_single_story_version_dummy_wrapper(story, 'version with a translation')
        self.helper_create_single_story_translation_dummy_wrapper(story_version, 'el', 'my greek version')
        self.helper_create_single_story_translation_dummy_wrapper(story_version, 'ru', 'my russian version')

        client = APIClient()
        client.force_authenticate(user=self.staff_user)
        list_response = client.get(reverse('story_translation_list', kwargs={'pk': story_version.id}))

        self.assertEqual(list_response.status_code, status.HTTP_200_OK)

        results = list_response.data['results']
        self.assertIsInstance(results, list)

        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]['title'], 'my greek version')
        self.assertEqual(results[1]['title'], 'my russian version')

    # MEMBER TESTS
    def test_get_translation(self):
        self.helper_create_dummy_users()
        self.helper_cleanup_projects()

        project = self.helper_create_single_project('getting a story translation project',
                                                    'getting a story translation project description',
                                                    [self.staff_user],
                                                    [self.staff_user])
        story = self.helper_create_single_story_dummy_wrapper('story with a version with a translation', project)
        story_version = self.helper_create_single_story_version_dummy_wrapper(story, 'version with a translation')
        story_translation = self.helper_create_single_story_translation_dummy_wrapper(story_version, 'el', 'my greek version')

        client = APIClient()
        client.force_authenticate(user=self.staff_user)
        get_response = client.get(reverse('story_translation_detail', kwargs={'pk': story_translation.id}))

        self.assertEqual(get_response.status_code, status.HTTP_200_OK)
        self.assertEqual(get_response.data['version'], story_translation.version.id)
        self.assertEqual(get_response.data['language_code'], story_translation.language_code)
        self.assertEqual(get_response.data['translator']['id'], story_translation.translator.id)
        self.assertEqual(get_response.data['title'], story_translation.title)
        self.assertEqual(get_response.data['text'], story_translation.text)

    def test_alter_translation(self):
        self.helper_create_dummy_users()
        self.helper_cleanup_projects()

        project = self.helper_create_single_project('altering a story translation project',
                                                    'altering a story translation project description',
                                                    [self.staff_user],
                                                    [self.staff_user])
        story = self.helper_create_single_story_dummy_wrapper('story with a version with a translation to be altered', project)
        story_version = self.helper_create_single_story_version_dummy_wrapper(story, 'version with a translation to be altered')
        story_translation = self.helper_create_single_story_translation_dummy_wrapper(story_version, 'el', 'my greek version')

        data = {'version': story_version.id,
                'language_code': 'ru',
                'translator': self.staff_user.id,
                'verified': 0,
                'live': 0,
                'title': 'my great russian title',
                'text': 'my great russian text'}
        client = APIClient()
        client.force_authenticate(user=self.staff_user)
        alter_response = client.put(reverse('story_translation_detail', kwargs={'pk': story_translation.id}), data, format='json')

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

        project = self.helper_create_single_project('deleting a story translation project',
                                                    'deleting a story translation project',
                                                    [self.staff_user],
                                                    [self.staff_user])
        story = self.helper_create_single_story_dummy_wrapper('story with a version with a translation to be deleted', project)
        story_version = self.helper_create_single_story_version_dummy_wrapper(story, 'version with a translation to be deleted')
        story_translation = self.helper_create_single_story_translation_dummy_wrapper(story_version, 'el', 'my greek version')

        client = APIClient()
        client.force_authenticate(user=self.staff_user)
        delete_response = client.delete(reverse('story_translation_detail', kwargs={'pk': story_translation.id}))

        self.assertEqual(delete_response.status_code, status.HTTP_204_NO_CONTENT)

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
                                                    'creating a project plan project description',
                                                    [self.staff_user],
                                                    [self.staff_user])
        story_1 = self.helper_create_single_story_dummy_wrapper('story for a project plan 1', project)
        story_2 = self.helper_create_single_story_dummy_wrapper('story for a project plan 2', project)

        data = {'project': project.id,
                'start_date': datetime.datetime.now().strftime("%Y-%m-%d"),
                'end_date': datetime.datetime.now().strftime("%Y-%m-%d"),
                'title': 'my api project plan',
                'description': 'my api project plan description',
                'responsible_users': [self.volunteer_user.id, self.user_user.id],
                'related_stories': [story_1.id, story_2.id],
                'order': 1}
        client = APIClient()
        client.force_authenticate(user=self.staff_user)
        create_response = client.post(reverse('project_plan_list', kwargs={'pk': project.id}), data, format='json')

        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)

        try:
            project_plan = ProjectPlan.objects.get(id=create_response.data['id'])
        except ProjectPlan.DoesNotExist:
            project_plan = None

        self.assertIsInstance(project_plan, ProjectPlan)
        self.assertGreater(1, self.helper_string_date_compare(data['start_date'], project_plan.start_date))
        self.assertGreater(1, self.helper_string_date_compare(data['end_date'], project_plan.end_date))
        self.assertEqual(project_plan.title, data['title'])
        self.assertEqual(project_plan.description, data['description'])
        self.assertEqual(self.helper_all_objects_in_list_by_id(project_plan.responsible_users.all(), [self.volunteer_user, self.user_user]), True)
        self.assertEqual(self.helper_all_objects_in_list_by_id(project_plan.related_stories.all(), [story_1, story_2]), True)
        self.assertEqual(project_plan.order, data['order'])

    def test_list_project_plans(self):
        self.helper_create_dummy_users()
        self.helper_cleanup_projects()

        project = self.helper_create_single_project('listing project plans project',
                                                    'listing a project plans project description',
                                                    [self.staff_user],
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
        list_response = client.get(reverse('project_plan_list', kwargs={'pk': project.id}))

        self.assertEqual(list_response.status_code, status.HTTP_200_OK)

        results = list_response.data['results']
        self.assertIsInstance(results, list)
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]['title'], 'my project plan 1')
        self.assertEqual(results[1]['title'], 'my project plan 2')

    #PROJECT PLAN MEMBERS
    def test_get_project_plan(self):
        self.helper_create_dummy_users()
        self.helper_cleanup_projects()

        project = self.helper_create_single_project('getting a project plan project',
                                                    'getting a projeect plan project description',
                                                    [self.staff_user],
                                                    [self.staff_user])
        story = self.helper_create_single_story_dummy_wrapper('story for a project plan get', project)
        project_plan = self.helper_create_single_project_plan_dummer_wrapper(project=project,
                                                                             title='my project plan',
                                                                             related_stories=[story],
                                                                             order=1)

        client = APIClient()
        client.force_authenticate(user=self.staff_user)
        get_response = client.get(reverse('project_plan_detail', kwargs={'pk': project_plan.id}))

        self.assertEqual(get_response.status_code, status.HTTP_200_OK)
        self.assertEqual(project_plan.id, get_response.data['id'])
        self.assertGreater(1, self.helper_string_date_compare(get_response.data['start_date'], project_plan.start_date))
        self.assertGreater(1, self.helper_string_date_compare(get_response.data['end_date'], project_plan.end_date))
        self.assertEqual(project_plan.title, get_response.data['title'])
        self.assertEqual(project_plan.description, get_response.data['description'])
        self.assertEqual(self.helper_all_objects_in_list_by_id(project_plan.responsible_users.all(), get_response.data['responsible_users']), True)
        self.assertEqual(self.helper_all_objects_in_list_by_id(project_plan.related_stories.all(), get_response.data['related_stories']), True)
        self.assertEqual(project_plan.order, get_response.data['order'])

    def test_alter_project_plan(self):
        self.helper_create_dummy_users()
        self.helper_cleanup_projects()

        project = self.helper_create_single_project('altering a project plan project',
                                                    'altering a project plan project description',
                                                    [self.staff_user],
                                                    [self.staff_user])
        story = self.helper_create_single_story_dummy_wrapper('story for a project plan alter', project)
        project_plan = self.helper_create_single_project_plan_dummer_wrapper(project=project,
                                                                             title='my project plan',
                                                                             related_stories=[story],
                                                                             order=1)
        story_1 = self.helper_create_single_story_dummy_wrapper('story for a project plan 1', project)

        data = {'project': project.id,
                'start_date': (datetime.datetime.now().date() + datetime.timedelta(10)).strftime("%Y-%m-%d"),
                'end_date': (datetime.datetime.now().date() + datetime.timedelta(10)).strftime("%Y-%m-%d"),
                'title': 'my altered title',
                'description': 'my altered description',
                'responsible_users': [self.volunteer_user.id, self.user_user.id],
                'related_stories': [story_1.id],
                'order': 5}
        client = APIClient()
        client.force_authenticate(user=self.staff_user)
        alter_response = client.put(reverse('project_plan_detail', kwargs={'pk': project_plan.id}), data, format='json')

        self.assertEqual(alter_response.status_code, status.HTTP_200_OK)

        project_plan = ProjectPlan.objects.get(id=project_plan.id)

        self.assertIsInstance(project_plan, ProjectPlan)
        self.assertGreater(1, self.helper_string_date_compare(alter_response.data['start_date'], project_plan.start_date))
        self.assertGreater(1, self.helper_string_date_compare(alter_response.data['end_date'], project_plan.end_date))
        self.assertEqual(project_plan.title, data['title'])
        self.assertEqual(project_plan.description, data['description'])
        self.assertEqual(self.helper_all_objects_in_list_by_id(project_plan.responsible_users.all(), [self.volunteer_user, self.user_user]), True)
        self.assertEqual(self.helper_all_objects_in_list_by_id(project_plan.related_stories.all(), [story_1]), True)
        self.assertEqual(project_plan.order, data['order'])

    def test_delete_project_plan(self):
        self.helper_create_dummy_users()
        self.helper_cleanup_projects()

        project = self.helper_create_single_project('deleting a project plan project',
                                                    'deleting a project plan project description',
                                                    [self.staff_user],
                                                    [self.staff_user])
        story = self.helper_create_single_story_dummy_wrapper('story for a project plan delete', project)
        project_plan = self.helper_create_single_project_plan_dummer_wrapper(project=project,
                                                                             title='my project plan',
                                                                             related_stories=[story],
                                                                             order=1)

        client = APIClient()
        client.force_authenticate(user=self.staff_user)
        delete_response = client.delete(reverse('project_plan_detail', kwargs={'pk': project_plan.id}))

        self.assertEqual(delete_response.status_code, status.HTTP_204_NO_CONTENT)

        try:
            project_plan = ProjectPlan.objects.get(id=project_plan.id)
        except ProjectPlan.DoesNotExist:
            project_plan = None

        self.assertEqual(project_plan, None)

    # -- PROJECT HELPER FUNCTIONS
    #
    #
    def helper_create_single_project(self, title, description, coordinators, users):
        project = Project(title=title,
                          description=description)
        project.save()
        project.coordinators.add(*coordinators)
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
                                                      start_date=datetime.datetime.now().date(),
                                                      end_date=datetime.datetime.now().date() + datetime.timedelta(7),
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
    def helper_create_single_story(self, project, title, thesis="", reporters=[], researchers=[], editors=[], copy_editors=[], fact_checkers=[], translators=[], artists=[]):
        story = Story(project=project, title=title, thesis="", published=datetime.datetime.now())
        story.save()
        if len(reporters) > 0:
            story.reporters.add(*reporters)
        if len(researchers) > 0:
            story.researchers.add(*researchers)
        if len(editors) > 0:
            story.editors.add(*editors)
        if len(copy_editors) > 0:
            story.copy_editors.add(*copy_editors)
        if len(fact_checkers) > 0:
            story.fact_checkers.add(*fact_checkers)
        if len(translators) > 0:
            story.translators.add(*translators)
        if len(artists) > 0:
            story.artists.add(*artists)
        story.save()
        story = Story.objects.get(id=story.id)

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

    def helper_create_single_story_version(self, story, timestamp=None, author=None, title="", text=""):
        story_version = StoryVersion(story=story,
                                     title=title,
                                     text=text)
        if timestamp is None:
            story_version.timestamp = datetime.datetime.now()

        if author is not None:
            story_version.author = author

        story_version.save()

        return story_version

    def helper_create_single_story_version_dummy_wrapper(self, story, title):
        self.helper_set_story_dummy_participants()
        return self.helper_create_single_story_version(story=story,
                                                       timestamp=datetime.datetime.now(),
                                                       author=self.dummy_version_author,
                                                       title=title,
                                                       text='im a dummy story version')

    def helper_create_single_story_translation(self, version, language_code="en", translator=None, verified=False, live=False, title="", text=""):
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

    def helper_string_datetime_compare(self, string, datetime_object):
        try:
            string_datetime = datetime.datetime.strptime(string, "%Y-%m-%dT%H:%M:%SZ")
        except ValueError as e:
            string_datetime = datetime.datetime.strptime(string, "%Y-%m-%dT%H:%M:%S.%fZ")

        return (string_datetime - datetime_object.replace(tzinfo=None)).total_seconds()

    def helper_string_date_compare(self, string, date_object):
        string_date = datetime.datetime.strptime(string, "%Y-%m-%d").date()

        return (string_date - date_object).total_seconds()

    def helper_datetime_datetime_compare(self, datetime_object_1, datetime_object_2):
        return (datetime_object_1 - datetime_object_2).total_seconds()

    def helper_create_dummy_users(self):
        self.staff_user = get_user_model().objects.get(email=self.staff_email)
        self.admin_user = get_user_model().objects.get(email=self.admin_email)
        self.volunteer_user = get_user_model().objects.get(email=self.volunteer_email)
        self.user_user = get_user_model().objects.get(email=self.user_email)
        self.user2_user = get_user_model().objects.get(email=self.user2_email)

    def helper_all_objects_in_list_by_id(self, users, ids):
        """
        users is a list of django user objects
        ids assumes a multidimensional list of dicts OR list of users
        """

        num_users = len(users)
        num_users_found = 0

        if len(ids) != len(users):
            return False

        for user in users:
            for i in ids:

                if isinstance(i, dict):
                    if user.id == i['id']:
                        num_users_found += 1
                        break
                elif isinstance(i, int) or isinstance(i, long):
                    if user.id == i:
                        num_users_found += 1
                        break
                else:
                    # assume user objects
                    if user.id == i.id:
                        num_users_found += 1
                        break

        if num_users == num_users_found:
            return True

        return False

    #
    #

    # def test_assign_editor(self):
    #     pass

    # def test_unassign_editor(self):
    #     pass

    # def test_assign_journalist(self):
    #     pass

    # def test_unassign_journalist(self):
    #     pass

    # def test_assign_researcher(self):
    #     pass

    # def test_unassign_researcher(self):
    #     pass

    # def test_assign_copyeditor(self):
    #     pass

    # def test_unassign_copyeditor(self):
    #     pass

    # def test_assign_translator(self):
    #     pass

    # def test_unassign_translator(self):
    #     pass

    # def test_assign_artist(self):
    #     pass

    # def test_unassign_artist(self):
    #     pass

    # def test_set_story_status(self):
    #     pass

    # def test_publish_story(self):
    #     pass

    # def test_unpublish_story(self):
    #     pass

    # def test_write_story(self):
    #     pass

    # def test_add_art(self):
    #     pass

    # def test_add_documents(self):
    #     pass

    # def test_prioritize_stories(self):
    #     pass

    # def test_add_comment(self):
    #     pass

    # def test_edit_comment(self):
    #     pass

    # def test_remove_comment(self):
    #     pass

    # def test_lock_story(self):
    #     pass
