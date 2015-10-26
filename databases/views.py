from django.db.models import Count
from django.views.generic import ListView

from core.countries import COUNTRIES
from databases.fixtures import DATABASE_TYPES
from databases.models import ExternalDatabase
from databases.forms import CountryFilterForm


class ExternalDatabaseList(ListView):
    template_name = "external_databases.jinja"
    model = ExternalDatabase

    def get_queryset(self):
        country = self.request.GET.get('country')
        if country:
            query = ExternalDatabase.objects.filter(country=country)
        else:
            query = ExternalDatabase.objects.all()

        return query.order_by("agency")

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
