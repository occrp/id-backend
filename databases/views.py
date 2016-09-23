from collections import namedtuple

from django.shortcuts import render
from django.db.models import Count

from .models import ExternalDatabase, DATABASE_TYPES, DATABASE_COUNTRIES
from .models import get_region

Country = namedtuple('Country', ['code', 'name', 'region', 'count'])
Type = namedtuple('Type', ['code', 'name', 'count'])
COUNTRY_NAMES = dict(DATABASE_COUNTRIES)
TYPE_NAMES = dict(DATABASE_TYPES)


def index(request):
    q = ExternalDatabase.objects.values('country')
    q = q.annotate(num=Count('country'))
    countries = []
    for row in q:
        country = row.get('country')
        region = get_region(country)
        if region is None:
            continue
        countries.append(Country(code=country,
                                 name=COUNTRY_NAMES.get(country),
                                 region=region,
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
    print list(q)
    return render(request, 'topic.jinja', {
        'count': q.count(),
        'db_type': db_type,
        'db_type_name': TYPE_NAMES.get(db_type),
        'databases': q
    })
