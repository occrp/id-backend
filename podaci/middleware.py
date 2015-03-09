from django.shortcuts import render_to_response
import elasticsearch


class PodaciExceptionMiddleware(object):
    def process_exception(self, request, exception):
        if isinstance(exception, elasticsearch.ConnectionError):
            return render_to_response("podaci/errors/connectionerror.jinja", {"request": request, "user": request.user})
        elif isinstance(exception, elasticsearch.ConnectionTimeout):
            return render_to_response("podaci/errors/connectiontimeout.jinja", {"request": request, "user": request.user})
        elif isinstance(exception, elasticsearch.NotFoundError):
            return render_to_response("podaci/errors/notfound.jinja", {"request": request, "user": request.user})
        elif isinstance(exception, elasticsearch.RequestError):
            return render_to_response("podaci/errors/requesterror.jinja", {"request": request, "user": request.user})

