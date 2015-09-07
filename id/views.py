from registration.views import RegistrationView
from settings.settings import REGISTRATION_OPEN, REGISTRATION_CLOSED_URL, REGISTRATION_SUCCESS_URL
from django.contrib.auth.views import logout as django_logout
from django.contrib.auth.views import REDIRECT_FIELD_NAME

from django.http import HttpResponseRedirect
from id.forms import FeedbackForm

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.http import JsonResponse

from id.models import Notification

class ProfileRegistrationView(RegistrationView):
    """
    Profile registration view.
    as per http://django-registration.readthedocs.org/en/latest/views.html
    """

    disallowed_url = REGISTRATION_CLOSED_URL
    success_url = REGISTRATION_SUCCESS_URL


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


def logout(request, next_page=None,
           template_name='registration/logged_out.html',
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


class NotificationSeen(APIView):
    permission_classes = (IsAuthenticated, )

    def get(self, request, *args, **kwargs):
        nid = kwargs.get('pk')
        if nid == "all":
            nots = Notification.objects.filter(user=request.user)
            for n in nots:
                n.seen()
            return JsonResponse({
                "action": "seen",
                "notifications": [n.id for n in nots],
                "unseen_count": Notification.objects.filter(user=request.user, is_seen=False).count()
            })
        else:
            try:
                notification = Notification.objects.get(
                    pk=nid,
                    user=request.user
                )
            except Exception, e:
                return JsonResponse({"error": e})

            notification.seen()
            return JsonResponse({
                "action": "seen",
                "notifications": [notification.id],
                "unseen_count": Notification.objects.filter(user=request.user, is_seen=False).count()
            })


class NotificationStream(APIView):
    # serializer_class = NotificationSerializer
    permission_classes = (IsAuthenticated, )

    pass
