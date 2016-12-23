import logging
from urlparse import urljoin
from collections import namedtuple
import requests
from django.shortcuts import render
from django.db.models import Count
from django.conf import settings

from .models import ExternalDatabase, get_regions
from .models import DATABASE_TYPES, DATABASE_COUNTRIES, EXPAND_REGIONS

log = logging.getLogger(__name__)

Country = namedtuple('Country', ['code', 'name', 'regions', 'count'])
Type = namedtuple('Type', ['code', 'name', 'count'])
COUNTRY_NAMES = dict(DATABASE_COUNTRIES)
TYPE_NAMES = dict(DATABASE_TYPES)
ALEPH_METADATA = {}


def get_aleph_metadata():
    if not len(ALEPH_METADATA):
        try:
            res = requests.get(urljoin(settings.ALEPH_URL, '/api/1/metadata'))
            ALEPH_METADATA.update(res.json())
        except Exception as ex:
            log.exception(ex)
    return ALEPH_METADATA


def get_databases_index():
    q = ExternalDatabase.objects.values('country')
    q = q.annotate(num=Count('country'))
    countries = []
    for row in q:
        country = row.get('country')
        if not len(country):
            continue
        regions = get_regions(country)
        countries.append(Country(code=country,
                                 name=COUNTRY_NAMES.get(country, country),
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
    return {
        'countries': countries,
        'country_names': COUNTRY_NAMES,
        'regions': EXPAND_REGIONS.keys(),
        'types': types
    }


def index(request):
    return render(request, 'index.jinja', get_databases_index())


def country(request, country_code):
    q = ExternalDatabase.objects.all()
    q = q.filter(country=country_code)
    q = q.order_by("agency")

    try:
        # get collections from aleph
        url = urljoin(settings.ALEPH_URL, '/api/1/collections')
        res = requests.get(url, params={
            'countries': country_code.lower(),
            'limit': 100,
            'counts': 'true'
        })
        collections = res.json()
    except Exception as ex:
        log.exception(ex)
        collections = {'total': 0, 'results': []}

    return render(request, 'country.jinja', {
        'count': q.count(),
        'country_code': country_code,
        'country_name': COUNTRY_NAMES.get(country_code),
        'categories': get_aleph_metadata().get('categories', {}),
        'collections': collections,
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
