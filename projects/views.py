from django.http import HttpResponse

def dummy_view(request):
    html = ""
    return HttpResponse(html)
