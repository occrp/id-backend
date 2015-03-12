from django.shortcuts import render
import elasticsearch


class PodaciExceptionMiddleware(object):
    def process_exception(self, request, exception):
    	cr = {"request": request, "user": request.user}
        if isinstance(exception, elasticsearch.ConnectionError):
            return render(request, "podaci/errors/connectionerror.jinja", cr)
        elif isinstance(exception, elasticsearch.ConnectionTimeout):
            return render(request, "podaci/errors/connectiontimeout.jinja", cr)
        elif isinstance(exception, elasticsearch.NotFoundError):
            return render(request, "podaci/errors/notfound.jinja", cr)
        elif isinstance(exception, elasticsearch.RequestError):
            return render(request, "podaci/errors/requesterror.jinja", cr)

