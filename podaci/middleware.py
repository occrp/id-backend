from django.shortcuts import render
from pyes.exceptions import ElasticSearchException


class PodaciExceptionMiddleware(object):

    def process_exception(self, request, exception):
        cr = {"request": request, "user": request.user}
        if isinstance(exception, ElasticSearchException):
            return render(request, "podaci/error.jinja", cr)
