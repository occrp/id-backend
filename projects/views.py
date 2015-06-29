from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.http import JsonResponse
from django.http import Http404

from rest_framework import generics
from rest_framework import mixins
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
from rest_framework.reverse import reverse
from rest_framework.views import APIView

from projects.models import Project, Story
from projects.serializers import ProjectSerializer, StorySerializer, UserSerializer

import simplejson

# -- API ROOT
# -- general entry point for the api
#
@api_view(('GET',))
def api_root(request, format=None):
    return Response({
        'projects': reverse('project_list', request=request, format=format)
    })

# -- PROJECT VIEWS
#
#
class ProjectList(generics.ListCreateAPIView):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer

class ProjectDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer

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
class StoryList(generics.ListCreateAPIView):
    queryset = Story.objects.all()
    serializer_class = StorySerializer

    def get_queryset(self):
        try:
            project_id = int(self.kwargs['pk'])
            stories = Story.objects.filter(project__id=project_id)
        except Story.DoesNotExist:
            stories = []

        return stories

    def perform_create(self, serializer):
        serializer.save(podaci_root='somepodaciroot')

class StoryDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Story.objects.all()
    serializer_class = StorySerializer


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
