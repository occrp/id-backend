from django.utils.translation import to_locale, get_language
from django.core.urlresolvers import resolve
from django.utils import formats

def locale(request):
    lang = get_language()

    if lang == "en-us":
        lang = "en"
    return {
        'LOCALE': to_locale(get_language()),
        'LOCALE_LC': to_locale(get_language()).lower(),
        'LANGUAGE_LC': lang.lower(),
        'LANGUAGE_SHORT_DATE_FORMAT': formats.get_format("SHORT_DATE_FORMAT", lang=get_language())
    }


def routename(request):
    return {
        'ROUTE_NAME': resolve(request.path_info).url_name
    }
