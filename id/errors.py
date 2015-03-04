from django.shortcuts import render_to_response

def _400(request, **kwargs):
	return render_to_response("errors/400.jinja", {"request": request, "user": request.user})

def _403(request, **kwargs):
	return render_to_response("errors/403.jinja", {"request": request, "user": request.user})

def _404(request, **kwargs):
	return render_to_response("errors/404.jinja", {"request": request, "user": request.user})

def _500(request, **kwargs):
	return render_to_response("errors/500.jinja", {"request": request, "user": request.user})
