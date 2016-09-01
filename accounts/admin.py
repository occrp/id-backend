from django.views.generic import TemplateView

from core.utils import version
from ticket.models import Ticket, PersonTicket, CompanyTicket, OtherTicket
from ticket.models import TicketCharge
from .models import Network, AccountRequest, Profile


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
