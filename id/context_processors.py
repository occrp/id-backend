from django.utils.translation import to_locale, get_language
from django.core.urlresolvers import resolve
from id.models import Profile

def userprofile(request):
    if request.user.is_authenticated():
        try:
            prof = request.user.profile
            print "Got user profile!"
        except Exception, e:
            print "User profile for %s does not exist" % request.user.username
            prof = Profile(user=request.user)
            prof.save()
            print "Created profile!"
        return {
            'user_profile': prof
        }
    return {}

def locale(request):
    lang = get_language()
    if lang == "en-us":
        lang = "en"
    return {
        'LOCALE': to_locale(get_language()),
        'LOCALE_LC': to_locale(get_language()).lower(),
        'LANGUAGE_LC': lang.lower()
    }


def routename(request):
    return {
    	'ROUTE_NAME': resolve(request.path_info).url_name
    }


