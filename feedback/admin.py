from django.views.generic import TemplateView, CreateView
from django.http import HttpResponseRedirect

from id.models import Feedback
from .forms import FeedbackForm


class FeedbackAuthMixin(object):
    """
    if that's not an authenticated user asking for a feedback-related URL
    *and* there's no indication that we should accept feedback from them
    just redirect to feedback URL

    cleared_for_feedback should happen only for users that have just logged-out
    and will be cleared in FeedbackThanks
    """
    fallback_redirect_url = '/accounts/login/'

    def verify_feedback_auth(self, request):
        return (request.user.is_authenticated() or ('cleared_for_feedback' in request.session and request.session['cleared_for_feedback'] == True))

    def get(self, request, *args, **kwargs):
        if self.verify_feedback_auth(request):
            return super(FeedbackAuthMixin, self).get(request, *args, **kwargs)
        else:
            return HttpResponseRedirect(self.fallback_redirect_url)

    def post(self, request, *args, **kwargs):
        if self.verify_feedback_auth(request):
            return super(FeedbackAuthMixin, self).post(request, *args, **kwargs)
        else:
            return HttpResponseRedirect(self.fallback_redirect_url)


class Feedback(FeedbackAuthMixin, CreateView):
    model = Feedback
    form_class = FeedbackForm
    template_name = "admin/feedback.jinja"
    success_url = '/feedback/thankyou/'

    # fill-in initial data for logged-in users
    def get_initial(self):
        if self.request.user.is_authenticated():
            return {
                'email': self.request.user.email,
                'name' : ' '.join([self.request.user.first_name, self.request.user.last_name])
            }
        else:
            return {}

    def get_form(self, form_class):
        # if we have an authenticated user, we have the user data
        if self.request.user.is_authenticated():
            # copy the data, as it's immutable in request
            rdata = self.request.POST.copy()
            # handle the e-mail
            rdata['email'] = self.request.user.email
            # handle the name if needed
            if 'name' not in rdata or rdata['name'].strip() == '':
                rdata['name']  = ' '.join([self.request.user.first_name, self.request.user.last_name])
            # set it back
            self.request.POST = rdata
        return super(Feedback, self).get_form(form_class)


class FeedbackThanks(FeedbackAuthMixin, TemplateView):
    template_name = "admin/feedback_thanks.jinja"

    def remove_clearance(self, request, response):
        # remove the feedback clearance
        if 'cleared_for_feedback' in request.session:
            del request.session['cleared_for_feedback']
            response.request = request
        return response

    def get(self, request, *args, **kwargs):
        # get the response
        response = super(FeedbackThanks, self).get(request, *args, **kwargs)
        return self.remove_clearance(request, response)

    def post(self, request, *args, **kwargs):
        # get the response
        response = super(FeedbackThanks, self).post(request, *args, **kwargs)
        return self.remove_clearance(request, response)
