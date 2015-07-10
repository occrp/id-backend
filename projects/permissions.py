import rules
from rest_framework import permissions

class CanAlterDeleteProject(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):

        print "can view project"
        print request.user.has_perm('projects.can_view_project', obj)

        if request.method == "GET":
            print "in get"
            return request.user.has_perm('projects.can_view_project', obj)
        else:
            return request.user.has_perm('projects.can_alter_or_delete_project', obj)
