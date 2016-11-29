import urllib

from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse


def redirect_403(request):
    next_url = urllib.quote(request.get_full_path())
    url = '%s?next=%s' % (reverse('login'), next_url)
    return HttpResponseRedirect(url)