from django.core.exceptions import PermissionDenied
import rules


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


@rules.predicate
def is_staff(user):
    if user.is_authenticated():
        if user.is_superuser or user.is_staff:
            return True
    return False


@rules.predicate
def is_superuser(user):
    if user.is_authenticated():
        if user.is_superuser:
            return True
    return False


def activate_user(backend, user, response, *args, **kwargs):
    user.is_active = True
    user.save()
