from django.views.generic import *
from id.models import *
from id.forms import ScraperRequestForm

class Panel(TemplateView):
    template_name = "admin/panel.jinja"

class Storage(TemplateView):
    template_name = "admin/storage.jinja"

class Statistics(TemplateView):
    template_name = "admin/statistics.jinja"

    def get_context_data(self):
        return {
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
            "accounts_admin": Profile.objects.filter(is_admin=True).count(),
            "person_count": Person.objects.count(),
            "company_count": Company.objects.count(),
            "location_count": Location.objects.count(),
            "relationship_count": Relationship.objects.count(),
            "accreq_total": AccountRequest.objects.count(),
            "accreq_approved": AccountRequest.objects.filter(approved=True).count(),
            "accreq_rejected": AccountRequest.objects.filter(approved=False).count(),
            "accreq_outstanding": AccountRequest.objects.filter(approved=None).count(),
        }

class CompanyList(TemplateView):
    template_name = "crud/company/list.jinja"

class PersonList(TemplateView):
    template_name = "crud/person/list.jinja"

class LocationList(TemplateView):
    template_name = "crud/location/list.jinja"

class RelationshipList(TemplateView):
    template_name = "crud/relationship/list.jinja"


class DatabaseScrapeRequestCreate(CreateView):
    form_class = ScraperRequestForm
    template_name = "admin/database_scrape_request.jinja"
    success_url = '/admin/scrapers/request/'

    def get_context_data(self, **kwargs):
        kwargs['object_list'] = DatabaseScrapeRequest.objects.all()
        return super(DatabaseScrapeRequestCreate, self).get_context_data(**kwargs)
