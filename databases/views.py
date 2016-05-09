from django.db.models import Count
import django.forms
from django.views.generic import ListView, TemplateView
from rest_framework import generics, status
from rest_framework.response import Response

from core.countries import COUNTRIES
import databases
from databases.models import ExternalDatabase, DATABASE_TYPES, EXPAND_REGIONS
from databases.forms import CountryFilterForm, ExternalDatabaseForm
from databases.serializers import DatabaseSerializer
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from core.auth import IsAdminOrReadOnly


class ExternalDatabaseList(ListView):
    template_name = "external_databases.jinja"
    model = ExternalDatabase

    def get_queryset(self):
        filter = self.request.GET.get('filter', None)
        country = self.request.GET.get('country', None)
        db_type = self.request.GET.get('db_type', None)

        q = ExternalDatabase.objects.all()
        if country and len(country.strip()):
            expanded = EXPAND_REGIONS.get(country, [])
            q = q.filter(country__in=[country] + list(expanded))
        if db_type:
            q = q.filter(db_type=db_type)
        if filter:
            q = q.filter(agency__contains=filter)
        return q.order_by("agency")

    def get_context_data(self, **kwargs):
        context = super(ExternalDatabaseList, self).get_context_data(**kwargs)
        context["filter_form"] = CountryFilterForm(initial=self.request.GET)
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


class DatabaseCollectionView(generics.ListCreateAPIView):
    serializer_class = DatabaseSerializer
    permission_classes = (IsAdminOrReadOnly, )
    queryset = ExternalDatabase.objects.all()


class DatabaseMemberView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = DatabaseSerializer
    permission_classes = (IsAdminOrReadOnly, )
    queryset = ExternalDatabase.objects.all()


class DatabaseRequest(TemplateView):
    template_name = "database/request.jinja"

    def dispatch(self, *args, **kwargs):
        if (self.kwargs.has_key('db_id')):
            db_obj = ExternalDatabase.objects.get(pk=self.kwargs['db_id'])

        else:
            db_obj = ExternalDatabase()

        self.forms = {
            'register_form': databases.forms.ExternalDatabaseForm(
                instance=db_obj,
                prefix=''
            )
        }

        return super(DatabaseRequest, self).dispatch(self.request)

    def get_context_data(self):
        ctx = {
        }

        if (self.kwargs.has_key('db_id')):
            ctx['pk'] = self.kwargs['db_id']

        ctx.update(self.forms)

        return ctx

