from django.views.generic import *
from core.utils import file_to_str
from id.models import *
from ticket.models import *
from id.forms import ScraperRequestForm
from ticket.forms import BudgetForm
from podaci import FileSystem
from search.models import SearchRequest

class Panel(TemplateView):
    template_name = "admin/panel.jinja"

class Storage(TemplateView):
    template_name = "admin/storage.jinja"

    def get_context_data(self):
        fs = FileSystem(user=self.request.user)
        return {
            "podaci": fs.status()
        }

class Statistics(TemplateView):
    template_name = "admin/statistics.jinja"

    def get_context_data(self):
        return {
            "version": file_to_str('.git_current_version')
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
            "searches": SearchRequest().statistics(),
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
