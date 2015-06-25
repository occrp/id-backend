from django.http import HttpResponse
from django.http import JsonResponse

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer

import simplejson

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
