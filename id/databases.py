from django.db.models import Count
from django.views.generic import *
from id.models import ExternalDatabase
from id.forms import CountryFilterForm
import re

class ExternalDatabaseList(ListView):
    template_name = "external_databases.html"
    model = ExternalDatabase

    badre = re.compile("\[\'(.*)\'\]")

    def _fix_country(self, country):
        # for some reason, googlebot cooks up broken urls like
        # ?country=%5B'MD'%5D&_locale=en
        # turn them into real ones
        if self.badre.match(country):
            country = self.badre.match(country).group(1)
        return country

    def get_queryset(self):
        print self.request.GET
        country = self.request.GET.get('country')
        if country:
            print "Got country: %s" % country
            country = self._fix_country(country)
            query = ExternalDatabase.objects.filter(country=country)
        else:
            query = ExternalDatabase.objects.all()

        return query.order_by("agency")

    def get_context_data(self, **kwargs):
        context = super(ExternalDatabaseList, self).get_context_data(**kwargs)
        context["filter_form"] = CountryFilterForm()
        context["count"] = ExternalDatabase.objects.count()
        context["jurisdictions"] = (ExternalDatabase.objects.values("country")
                                    .annotate(total=Count('country'))
                                    .order_by('-total')[0]["total"])

        return context


class ExternalDatabaseDetail(DetailView):
    model = ExternalDatabase

class ExternalDatabaseDelete(DeleteView):
    model = ExternalDatabase

class ExternalDatabaseEdit(UpdateView):
    model = ExternalDatabase

class ExternalDatabaseAdd(CreateView):
    model = ExternalDatabase
