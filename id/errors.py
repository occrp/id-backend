from django.shortcuts import render_to_response

def _400(request, **kwargs):
	return render_to_response("errors/400.html", {"request": request, "user": request.user})

def _403(request, **kwargs):
	return render_to_response("errors/403.html", {"request": request, "user": request.user})

def _404(request, **kwargs):
	return render_to_response("errors/404.html", {"request": request, "user": request.user})

def _500(request, **kwargs):
	return render_to_response("errors/500.html", {"request": request, "user": request.user})
