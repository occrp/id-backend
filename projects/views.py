from django.http import HttpResponse

def dummy_view(request, id=0):
    html = ""
    return HttpResponse(html)
