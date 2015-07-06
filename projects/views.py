from django.contrib.auth import get_user_model
from django.db.models import Q
from django.http import HttpResponse
from django.http import JsonResponse
from django.http import Http404

from rest_framework import generics
from rest_framework import mixins as rest_framework_mixins
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
from rest_framework.reverse import reverse
from rest_framework.views import APIView

from projects.models import Project, Story, StoryVersion, StoryTranslation
from projects.mixins import (
    ProjectMembershipMixin, ProjectQuerySetMixin, StoryQuerySetMixin, StoryListQuerySetMixin,
    StoryVersionQuerySetMixin, StoryVersionListQuerySetMixin, StoryTranslationQuerySetMixin,
    StoryTranslationListQuerySetMixin, ProjectPlanQuerySetMixin, ProjectPlanListQuerySetMixin)
from projects.serializers import (
    ProjectSerializer, StorySerializer, UserSerializer, StoryVersionSerializer, StoryTranslationSerializer,
    ProjectPlanSerializer)

import simplejson

# -- API ROOT
# -- general entry point for the api
#
@api_view(('GET',))
def api_root(request, format=None):
    return Response({
        'projects': reverse('project_list', request=request, format=format),
        'stories': reverse('story_list', kwargs={'pk': 0}, request=request, format=format),
        'story detail': reverse('story_detail', kwargs={'pk': 0}, request=request, format=format),
        'story versions': reverse('story_version_list', kwargs={'pk': 0}, request=request, format=format),
        'story version detail': reverse('story_version_detail', kwargs={'pk': 0}, request=request, format=format),
        'story translations': reverse('story_translation_list', kwargs={'pk': 0}, request=request, format=format),
        'project plans': reverse('project_plan_list', kwargs={'pk': 0}, request=request, format=format),
        'project plan detail': reverse('project_plan_detail', kwargs={'pk': 0}, request=request, format=format)
    })

# -- USER VIEWS
#
#

class UsersBase(APIView):

    def get_object(self, pk):
        try:
            return get_user_model().objects.get(id=pk)
        except get_user_model().DoesNotExist:
            raise Http404

    def get_users_by_id_or_list(self, ids):

        users = []

        if isinstance(ids, int):
            users = [self.get_object(ids)]
        if isinstance(ids, list):
            for i in ids:
                users.append(self.get_object(i))

        return users

# -- PROJECT VIEWS
#
#
class ProjectList(ProjectQuerySetMixin, generics.ListCreateAPIView):
    serializer_class = ProjectSerializer

    def post(self, request, *args, **kwargs):
        request.data['coordinator'] = request.user.id
        return super(ProjectList, self).post(request, *args, **kwargs)


class ProjectDetail(ProjectQuerySetMixin, generics.RetrieveUpdateDestroyAPIView):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer

    def put(self, request, *args, **kwargs):
        request.data['coordinator'] = request.user.id
        return super(ProjectDetail, self).put(request, *args, **kwargs)

class ProjectUsers(UsersBase):

    def get_project(self, pk):
        try:
            return Project.objects.get(id=pk)
        except Project.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        project = self.get_project(pk)

        if len(project.users.all()) > 0:
            serializer = UserSerializer(project.users.all(), many=True)
            json = {'users': serializer.data}
            return Response(json)

        json = {'users': []}
        return Response(json)

    def put(self, request, pk, format=None):
        project = self.get_project(pk)
        user_ids = request.data['users']
        users = self.get_users_by_id_or_list(user_ids)

        try:
            project.users.add(*users)
        except:
            raise Http404

        serializer = UserSerializer(users, many=True)

        json = {'users': serializer.data}
        return Response(json)

    def delete(self, request, pk, format=None):
        project = self.get_project(pk)
        user_ids = request.data['users']
        users = self.get_users_by_id_or_list(user_ids)

        try:
            project.users.remove(*users)
        except:
            raise Http404

        return Response(status=status.HTTP_204_NO_CONTENT)

# -- STORY VIEWS
#
#
class StoryList(ProjectMembershipMixin, StoryListQuerySetMixin, generics.ListCreateAPIView):
    serializer_class = StorySerializer

    def get_queryset(self):
        return super(StoryList, self).get_queryset(self.kwargs['pk'])

    def perform_create(self, serializer):
        serializer.save(podaci_root='somepodaciroot')

    def post(self, request, *args, **kwargs):
        if not self.user_is_project_user(request.data['project'], request.user):
            return Response({'details': "not possible to use a project that does not exist or you don't belong to"},
                            status=status.HTTP_403_FORBIDDEN)

        return super(StoryList, self).post(request, *args, **kwargs)

class StoryDetail(ProjectMembershipMixin, StoryQuerySetMixin, generics.RetrieveUpdateDestroyAPIView):
    serializer_class = StorySerializer

    def put(self, request, *args, **kwargs):
        if not self.user_is_project_user(request.data['project'], request.user):
            return Response({'details': "not possible to change project to one that does not exist or you don't belong to"},
                            status=status.HTTP_403_FORBIDDEN)

        return super(StoryDetail, self).put(request, *args, **kwargs)

# -- STORY VERSION VIEWS
#
#
class StoryVersionList(StoryVersionListQuerySetMixin, generics.ListCreateAPIView):
    serializer_class = StoryVersionSerializer

    def get_queryset(self):
        return super(StoryVersionList, self).get_queryset(self.kwargs['pk'])

    def post(self, request, *args, **kwargs):
        if not self.user_is_story_user(request.data['story'], request.user):
            return Response({'details': "not possible to use a story that does not exist or you don't belong to"},
                            status=status.HTTP_403_FORBIDDEN)

        return super(StoryVersionList, self).post(request, *args, **kwargs)

class StoryVersionLive(APIView):

    def get(self, request, pk, language_code, format=None):
        story_versions = StoryVersion.objects.filter(story__id=pk).order_by('-timestamp', '-id')

        if story_versions.count() == 0:
            return Response({"details": "story not found"}, status=status.HTTP_404_NOT_FOUND)

        story_version = story_versions[0]

        translations = StoryTranslation.objects.filter(Q(version__id=story_version.id) &
                                                       Q(language_code=language_code) &
                                                       Q(live=True)).order_by("-timestamp")

        print story_version.title
        print story_version.timestamp

        if translations.count() == 0:
            return Response({"details": "translation for specified language not found"},
                            status=status.HTTP_404_NOT_FOUND)

        serializer = StoryTranslationSerializer(translations[0])
        return Response(serializer.data, status=status.HTTP_200_OK)


class StoryVersionDetail(StoryVersionQuerySetMixin, generics.RetrieveUpdateDestroyAPIView):
    serializer_class = StoryVersionSerializer

    def put(self, request, *args, **kwargs):
        if not self.user_is_story_user(request.data['story'], request.user):
            return Response({'details': "not possible to change story to one that does not exist or you don't belong to"},
                            status=status.HTTP_403_FORBIDDEN)

        return super(StoryVersionDetail, self).put(request, *args, **kwargs)

# -- STORY TRANSLATION VIEWS
#
#
class StoryTranslationList(StoryTranslationListQuerySetMixin, generics.ListCreateAPIView):
    serializer_class = StoryTranslationSerializer

    def get_queryset(self):
        return super(StoryTranslationList, self).get_queryset(self.kwargs['pk'])

    def post(self, request, *args, **kwargs):
        if not self.user_is_story_user(request.data['version'], request.user):
            return Response({'details': "not possible to use a story version that does not exist or you don't belong to"},
                            status=status.HTTP_403_FORBIDDEN)

        return super(StoryTranslationList, self).post(request, *args, **kwargs)

class StoryTranslationDetail(StoryTranslationQuerySetMixin, generics.RetrieveUpdateDestroyAPIView):
    serializer_class = StoryTranslationSerializer

    def put(self, request, *args, **kwargs):
        if not self.user_is_story_user(request.data['version'], request.user):
            return Response({'details': "not possible to change story version to one that does not exist or you don't belong to"},
                            status=status.HTTP_403_FORBIDDEN)

        return super(StoryTranslationDetail, self).put(request, *args, **kwargs)

# -- PROJECT PLAN VIEWS
#
#
class ProjectPlanList(ProjectPlanListQuerySetMixin, generics.ListCreateAPIView):
    serializer_class = ProjectPlanSerializer

    def get_queryset(self):
        return super(ProjectPlanList, self).get_queryset(self.kwargs['pk'])

    def post(self, request, *args, **kwargs):
        if not self.user_in_project(request.data['project'], request.user):
            return Response({'details': "not possible to use a project that does not exist or you don't belong to"},
                            status=status.HTTP_403_FORBIDDEN)

        if not self.stories_in_project(request.data['project'], request.data['related_stories']):
            return Response({'details': "not possible to use stories that do not exist or don't belong to the project"},
                            status=status.HTTP_403_FORBIDDEN)

        return super(ProjectPlanList, self).post(request, *args, **kwargs)

class ProjectPlanDetail(ProjectPlanQuerySetMixin, generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ProjectPlanSerializer

    def put(self, request, *args, **kwargs):
        if not self.user_in_project(request.data['project'], request.user):
            return Response({'details': "not possible to change to a project that does not exist or you don't belong to"},
                            status=status.HTTP_403_FORBIDDEN)

        if not self.stories_in_project(request.data['project'], request.data['related_stories']):
            return Response({'details': "not possible to use stories that do not exist or don't belong to the project"},
                            status=status.HTTP_403_FORBIDDEN)

        return super(ProjectPlanDetail, self).put(request, *args, **kwargs)

##

@api_view(['GET', 'POST', 'PUT', 'DELETE'])
def dummy_view(request, id=0):
    json = {'id': 0, 'title': 'dummy_view_title', 'coordinator': 0, 'users': []}
    return Response(json)

@api_view(['GET', 'POST', 'PUT', 'DELETE'])
def dummy_story_view(request, id=0, story_id=0, story_version_id=0):
    json = {'id': 0,
            'story': 0,
            'project_id': 0,
            'reporters': [],
            'researchers': [],
            'editors': [],
            'copy_editors': [],
            'fact_checkers': [],
            'translators': [],
            'artists': [],
            'published': '',
            'podaci_root': '',
            'versions': []
            }
    return Response(json)

@api_view(['GET', 'POST', 'PUT', 'DELETE'])
def dummy_translation_view(request, id=0, story_id=0, story_version_id=0, language_code='en'):
    json = {'id': 0,
            'version': 0,
            'language_code': 0,
            'timestamp': '',
            'translator': 0,
            'verified': True,
            'live': True,
            'title': '',
            'text': ''
            }
    return Response(json)

@api_view(['GET', 'POST', 'PUT', 'DELETE'])
def dummy_plan_view(request, id=0):
    json = {'id': 0,
            'project': 0,
            'start_date': 0,
            'end_date': 0,
            'title': '',
            'description': '',
            'responsible_users': [],
            'related_stories': [],
            'order': -1
            }
    return Response(json)
