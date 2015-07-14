from __future__ import absolute_import

import rules

from rest_framework import permissions

from projects.models import Project
import projects.rules

class CanAlterDeleteProject(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):

        if request.method in permissions.SAFE_METHODS:
            # filter will be done on the query set, so it is safe to return true here
            return True
        else:
            return request.user.has_perm('project.can_alter_or_delete_project', obj)

class CanCreateStory(permissions.BasePermission):

    def has_permission(self, request, view):

        if request.method in permissions.SAFE_METHODS:
            # filtering will be done on the queryset, so its safe to return true here
            return True
        else:
            try:
                obj = Project.objects.get(id=view.kwargs['pk'])
            except Exception as e:
                return False

            return request.user.has_perm('story.can_create_story', obj)

class CanAlterDeleteStory(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):

        if request.method in permissions.SAFE_METHODS:
            # filtering will be done on the queryset, so its safe to return true here
            return True
        else:
            return request.user.has_perm('story.can_alter_or_delete_story', obj)
