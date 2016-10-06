from collections import namedtuple

from django.shortcuts import render
from django.db.models import Count

from .models import ExternalDatabase, get_regions
from .models import DATABASE_TYPES, DATABASE_COUNTRIES, EXPAND_REGIONS

Country = namedtuple('Country', ['code', 'name', 'regions', 'count'])
Type = namedtuple('Type', ['code', 'name', 'count'])
COUNTRY_NAMES = dict(DATABASE_COUNTRIES)
TYPE_NAMES = dict(DATABASE_TYPES)


def index(request):
    q = ExternalDatabase.objects.values('country')
    q = q.annotate(num=Count('country'))
    countries = []
    for row in q:
        country = row.get('country')
        regions = get_regions(country)
        if not len(regions):
            continue
        countries.append(Country(code=country,
                                 name=COUNTRY_NAMES.get(country),
                                 regions=regions,
                                 count=row.get('num')))

    q = ExternalDatabase.objects.values('db_type')
    q = q.annotate(num=Count('db_type'))
    types = []
    for row in q:
        db_type = row.get('db_type')
        if db_type is None or not len(db_type):
            continue
        types.append(Type(code=db_type,
                          name=TYPE_NAMES.get(db_type),
                          count=row.get('num')))
    return render(request, 'index.jinja', {
        'count': ExternalDatabase.objects.count(),
        'countries': countries,
        'country_names': COUNTRY_NAMES,
        'regions': EXPAND_REGIONS.keys(),
        'types': types
    })


def country(request, country_code):
    q = ExternalDatabase.objects.all()
    q = q.filter(country=country_code)
    q = q.order_by("agency")
    return render(request, 'country.jinja', {
        'count': q.count(),
        'country_code': country_code,
        'country_name': COUNTRY_NAMES.get(country_code),
        'databases': q
    })


def topic(request, db_type):
    q = ExternalDatabase.objects.all()
    q = q.filter(db_type=db_type)
    q = q.order_by("agency")
    return render(request, 'topic.jinja', {
        'count': q.count(),
        'db_type': db_type,
        'db_type_name': TYPE_NAMES.get(db_type),
        'databases': q
    })
