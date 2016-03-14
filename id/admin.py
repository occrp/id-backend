from django.views.generic import *
from core.utils import version
from id.models import *
from ticket.models import *
from podaci.models import *
from id.forms import ScraperRequestForm, FeedbackForm
from ticket.forms import BudgetForm
from settings import settings
from django.db.models import Sum
from django.http import HttpResponseRedirect

class Panel(TemplateView):
    template_name = "admin/panel.jinja"

    def get_context_data(self):
        return {
            "admin_stream": (Notification.objects
                                .order_by("-timestamp"))
        }

class Storage(TemplateView):
    template_name = "admin/storage.jinja"

    def get_context_data(self):
        return {
            "podaci_files": PodaciFile.objects.count(),
            "podaci_tags": PodaciTag.objects.count(),
            "podaci_collections": PodaciCollection.objects.count(),
            "podaci_size": PodaciFile.objects.all().aggregate(Sum('size'))['size__sum'],
            "podaci_data_root": settings.PODACI_FS_ROOT,
            "podaci_data_sharding": "%d deep, %d long" % (HASH_DIRS_DEPTH, HASH_DIRS_LENGTH),
            "podaci_index": "None"
        }

class Statistics(TemplateView):
    template_name = "admin/statistics.jinja"

    def get_context_data(self):
        return {
            "version": version(),
            "tickets_opened": Ticket.objects.count(),
            "tickets_people": PersonTicket.objects.count(),
            "tickets_company": CompanyTicket.objects.count(),
            "tickets_other": OtherTicket.objects.count(),
            "tickets_closed": Ticket.objects.filter(status="closed").count(),
            "tickets_in_progress": Ticket.objects.filter(status="new").count(),
            "accounts_approved": Profile.objects.filter(is_user=True).count(),
            "accounts_user": Profile.objects.filter(is_user=True).count(),
            "accounts_volunteer": Profile.objects.filter(is_volunteer=True).count(),
            "accounts_staff": Profile.objects.filter(is_staff=True).count(),
            "accounts_admin": Profile.objects.filter(is_superuser=True).count(),
            "accreq_total": AccountRequest.objects.count(),
            "accreq_approved": AccountRequest.objects.filter(approved=True).count(),
            "accreq_rejected": AccountRequest.objects.filter(approved=False).count(),
            "accreq_outstanding": AccountRequest.objects.filter(approved=None).count(),
            "networks": Network.objects.all(),
            "unaffiliated_costs_total": sum([x.cost for x in TicketCharge.objects.filter(user__network=0)]),
            "unaffiliated_users_count": Profile.objects.filter(network=None).count()
        }


class DatabaseScrapeRequestCreate(CreateView):
    form_class = ScraperRequestForm
    template_name = "admin/database_scrape_request.jinja"
    success_url = '/admin/scrapers/request/'

    def get_context_data(self, **kwargs):
        kwargs['object_list'] = DatabaseScrapeRequest.objects.all()
        return super(DatabaseScrapeRequestCreate, self).get_context_data(**kwargs)


class Budgets(CreateView):
    form_class = BudgetForm
    template_name = "admin/budgets.jinja"
    success_url = '/admin/budgets'

    def get_context_data(self, **kwargs):
        kwargs['object_list'] = Budget.objects.all()
        return super(CreateView, self).get_context_data(**kwargs)


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
