from django.db.models import Count
from django.views.generic import *
from id.countries import COUNTRIES
from id.models import ExternalDatabase
from id.forms import CountryFilterForm
import re

class ExternalDatabaseList(ListView):
    template_name = "external_databases.jinja"
    model = ExternalDatabase

    badre = re.compile("\[\'(.*)\'\]")

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
        try:
            context["jurisdictions"] = (ExternalDatabase.objects.values("country")
                                        .annotate(total=Count('country'))
                                        .order_by('-total')[0]["total"])
        except IndexError, e:
            context["jurisdictions"] = 0

        return context


class ExternalDatabaseDetail(DetailView):
    model = ExternalDatabase

class ExternalDatabaseDelete(DeleteView):
    model = ExternalDatabase

class ExternalDatabaseEdit(UpdateView):
    model = ExternalDatabase

class ExternalDatabaseAdd(CreateView):
    model = ExternalDatabase
