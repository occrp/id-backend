from django.core.exceptions import PermissionDenied
from rest_framework import permissions


class IsAtLeastStaffOrReadOnly(permissions.BasePermission):
    """Allow unsafe methods only for those who are at least staff user."""

    def has_permission(self, request, view):
        if request.user.is_superuser:
            return True

        if request.user.is_staff:
            return True

        if request.method in permissions.SAFE_METHODS:
            return True

        return False


def perm(perm, view, **viewkwargs):
    assert(perm in ["any", "user", "staff", "admin"])

    def decorator(request, **reqkwargs):
        if perm != "any":
            user = request.user
            if not user.is_authenticated():
                raise PermissionDenied
            if perm == "admin" and not user.is_superuser:
                raise PermissionDenied
            elif perm == "staff" and not (user.is_superuser or user.is_staff):
                raise PermissionDenied

        return view.as_view(**viewkwargs)(request, **reqkwargs)

    return decorator


def require_admin(user):
    if not user.is_authenticated():
        raise PermissionDenied
    if user.is_superuser:
        return True
    raise PermissionDenied


def require_staff(user):
    if not user.is_authenticated():
        raise PermissionDenied
    if user.is_superuser:
        return True
    if user.is_staff:
        return True
    raise PermissionDenied


def activate_user(backend, user, response, *args, **kwargs):
    user.is_active = True
    user.save()
