from registration.views import RegistrationView
from settings.settings import REGISTRATION_OPEN, REGISTRATION_CLOSED_URL, REGISTRATION_SUCCESS_URL
from django.contrib.auth.views import logout as django_logout
from django.contrib.auth.views import login as django_login
from django.contrib.auth.views import REDIRECT_FIELD_NAME, AuthenticationForm

from django.http import HttpResponseRedirect
from id.forms import FeedbackForm
import logging
logger = logging.getLogger(__name__)


class ProfileRegistrationView(RegistrationView):
    """
    Profile registration view.
    as per http://django-registration.readthedocs.org/en/latest/views.html
    """

    disallowed_url = REGISTRATION_CLOSED_URL
    success_url = REGISTRATION_SUCCESS_URL
    fallback_redirect_url = '/'

    def registration_allowed(self, request):
        """
        Simple as that -- and controlled from settings
        """
        return REGISTRATION_OPEN

    def register(self, request, form):
        """
        Implement user-registration logic here. Access to both the
        request and the full cleaned_data of the registration form is
        available here.

        """
        return form.save()

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            return HttpResponseRedirect(self.fallback_redirect_url)
        else:
            return super(ProfileRegistrationView, self).dispatch(request, *args, **kwargs)


def logout(request, next_page=None,
           template_name='registration/logout.jinja',
           redirect_field_name=REDIRECT_FIELD_NAME,
           current_app=None, extra_context=None,
           form_class=FeedbackForm,
           fallback_redirect_url='/login'):
    """
    Overloading the logout() function from django.contrib.auth.views
    to provide confirmation that a user has actually just logged-out
    for our feedback form
    """
    if request.user.is_authenticated() or ('cleared_for_feedback' in request.session and request.session['cleared_for_feedback'] == True):

        # get the feedback form
        form = FeedbackForm()

        # add it to the template context
        if extra_context is not None:
            extra_context.update({
                'form': form
            })
        else:
            extra_context = {
                'form': form
            }

        # get the result
        result = django_logout(request, next_page, template_name, redirect_field_name, current_app, extra_context)

        # make sure we can proceed with feedback if we need to
        # for instance, if the form is not complete
        request.session['cleared_for_feedback'] = True
        result.request = request

        # return the whole thing
        return result

    else:
        return HttpResponseRedirect(fallback_redirect_url)


def login(request, template_name='registration/login.jinja',
          redirect_field_name=REDIRECT_FIELD_NAME,
          authentication_form=AuthenticationForm,
          current_app=None,
          extra_context=None,
          fallback_redirect_url='/'):
    """
    Overloading the login() function from django.contrib.auth.views
    to redirect logged-in users somewhere else
    """
    if request.user.is_authenticated():
        return HttpResponseRedirect(fallback_redirect_url)
    else:
        return django_login(request, template_name, redirect_field_name,
                            authentication_form, current_app, extra_context)


from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.core.signals import request_finished
from django.dispatch import receiver


@receiver(user_logged_in)
def recv_signal_user_logged_in(sender, user, **kwargs):
    logger.info("Logged in: user %s" % (user.email), extra={'user': user})


@receiver(user_logged_out)
def recv_signal_user_logged_out(sender, user, **kwargs):
    logger.info("Logged out: user %s" % (user.email), extra={'user': user})
