from django.shortcuts import render

from core.countries import COUNTRIES

from .models import ExternalDatabase, DATABASE_TYPES, EXPAND_REGIONS
from .forms import CountryFilterForm


def index(request):
    text = request.GET.get('filter', None)
    country = request.GET.get('country', None)
    db_type = request.GET.get('db_type', None)

    q = ExternalDatabase.objects.all()
    if country and len(country.strip()):
        expanded = EXPAND_REGIONS.get(country, [])
        q = q.filter(country__in=[country] + list(expanded))
    if db_type:
        q = q.filter(db_type=db_type)
    if text:
        q = q.filter(agency__contains=text)
    q = q.order_by("agency")
    return render(request, 'databases_index.jinja', {
        'filter_form': CountryFilterForm(initial=request.GET),
        'count': ExternalDatabase.objects.count(),
        'countries': dict(COUNTRIES),
        'database_types': dict(DATABASE_TYPES),
        'databases': q
    })
