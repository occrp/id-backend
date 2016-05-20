from django.utils.translation import to_locale, get_language
from django.core.urlresolvers import resolve
from django.utils import formats
from django.conf import settings # import the settings file

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

# template context preprocessors
#
# as per:
# http://stackoverflow.com/questions/433162/can-i-access-constants-in-settings-py-from-templates-in-django#433255
#

# debug, we might need it in the templates
def debug(request):
    # return the value you want as a dictionnary. you may add multiple values in there.
    return {
        'DEBUG': settings.DEBUG,
        'EMERGENCY': settings.EMERGENCY
    }
