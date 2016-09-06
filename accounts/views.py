import logging
from registration.views import RegistrationView

from django.contrib.auth.views import logout as django_logout
from django.contrib.auth.views import login as django_login
from django.contrib.auth.views import REDIRECT_FIELD_NAME, AuthenticationForm
from django.http import HttpResponseRedirect, JsonResponse

from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from settings.settings import REGISTRATION_OPEN, REGISTRATION_CLOSED_URL
from settings.settings import REGISTRATION_SUCCESS_URL

from core.models import Notification

logger = logging.getLogger(__name__)


class Profile(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        groups = []
        if request.user.is_staff:
            groups.append({
                'id': 'occrp_staff',
                'name': 'OCCRP staff'
            })
        if request.user.network:
            groups.append({
                'id': 'group:%d' % request.user.network.id,
                'name': request.user.network.long_name
            })
        return JsonResponse({
            'id': request.user.id,
            'email': request.user.email,
            'display_name': request.user.display_name,
            'is_admin': request.user.is_superuser,
            'groups': groups,
            'locale': request.user.locale,
            'country': request.user.country,
            'notifications_unseen': Notification.objects.filter(user=request.user, is_seen=False).count(),
            'notification_subscriptions': [x.channel for x in request.user.notificationsubscription_set.all()]
        })


class ProfileRegistrationView(RegistrationView):
    """Profile registration view.

    as per http://django-registration.readthedocs.org/en/latest/views.html
    """

    disallowed_url = REGISTRATION_CLOSED_URL
    success_url = REGISTRATION_SUCCESS_URL
    fallback_redirect_url = '/'

    def registration_allowed(self, request):
        """Simple as that -- and controlled from settings."""
        return REGISTRATION_OPEN

    def register(self, request, form):
        """Implement user-registration logic here.

        Access to both the request and the full cleaned_data of the registration
        form is available here.
        """
        return form.save()

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            return HttpResponseRedirect(self.fallback_redirect_url)
        else:
            return super(ProfileRegistrationView, self).dispatch(request, *args, **kwargs)


def logout(request):
    """Log out the current user.

    Overloading the logout() function from django.contrib.auth.views
    to provide confirmation that a user has actually just logged-out
    for our feedback form
    """
    django_logout(request)
    return HttpResponseRedirect('/')


def login(request, template_name='registration/login.jinja',
          redirect_field_name=REDIRECT_FIELD_NAME,
          authentication_form=AuthenticationForm,
          current_app=None,
          extra_context=None):
    """Show a form for the user to sign in.

    Overloading the login() function from django.contrib.auth.views
    to redirect logged-in users somewhere else
    """
    if request.user.is_authenticated():
        return HttpResponseRedirect('/')
    else:
        return django_login(request, template_name, redirect_field_name,
                            authentication_form, current_app, extra_context)
