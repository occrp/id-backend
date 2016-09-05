from django.shortcuts import render_to_response


def _400(request, **kwargs):
	return return_error(400, request, **kwargs)


def _401(request, **kwargs):
	return return_error(401, request, **kwargs)


def _403(request, **kwargs):
	return return_error(403, request, **kwargs)


def _404(request, **kwargs):
	return return_error(404, request, **kwargs)


def _500(request, **kwargs):
	return return_error(500, request, **kwargs)


def return_error(code, request, **kwargs):
    user = None
    try:
        user = request.user
    except AttributeError:
        pass

    return render_to_response("errors/%s.jinja" % code, {"request": request, "user": user})
