from django.db.models import Count
from django.views.generic import ListView

from core.countries import COUNTRIES
from databases.models import ExternalDatabase, DATABASE_TYPES, EXPAND_REGIONS
from databases.forms import CountryFilterForm


class ExternalDatabaseList(ListView):
    template_name = "external_databases.jinja"
    model = ExternalDatabase

    def get_queryset(self):
        country = self.request.GET.get('country')
        q = ExternalDatabase.objects.all()
        if len(country.strip()):
            expanded = EXPAND_REGIONS.get(country, [])
            q = q.filter(country__in=[country] + list(expanded))
        return q.order_by("agency")

    def get_context_data(self, **kwargs):
        context = super(ExternalDatabaseList, self).get_context_data(**kwargs)
        context["filter_form"] = CountryFilterForm()
        context["count"] = ExternalDatabase.objects.count()
        context["countries"] = dict(COUNTRIES)
        context["database_types"] = dict(DATABASE_TYPES)
        try:
            context["jurisdictions"] = (ExternalDatabase.objects.values("country")
                                        .annotate(total=Count('country'))
                                        .order_by('-total')[0]["total"])
        except IndexError:
            context["jurisdictions"] = 0

        return context
