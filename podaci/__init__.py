from django.http import HttpResponse
from django.views.generic import TemplateView
from django.contrib.auth.models import User
from id.mixins import JSONResponseMixin
from id.decorators import staff_only
from id.apis.podaci import *
import json
# from settings import PODACI_SERVERS, PODACI_ES_INDEX, PODACI_FS_ROOT

PODACI_SERVERS = [{"host": "localhost"}]
PODACI_ES_INDEX = "podaci"
PODACI_FS_ROOT = "/home/smari/Projects/OCCRP/data/"

class PodaciView(TemplateView, JSONResponseMixin):
    def dispatch(self, *args, **kwargs):
        # All of podaci is for staff only.
        staff_only(self.request.user)
        self.fs = FileSystem(
            PODACI_SERVERS, PODACI_ES_INDEX, 
            PODACI_FS_ROOT, self.request.user)
        return super(PodaciView, self).dispatch(*args, **kwargs)

    def post(self, request):
        return self.json_response()

    def get(self, request, **kwargs):
        format = request.GET.get("format", "html")
        print format
        if format != "json":
            return TemplateView.get(self, request, **kwargs)
        else:
            return self.json_response(**kwargs)

    def json_response(self, **kwargs):
        "Convert the context dictionary into a JSON object"
        # Note: This is *EXTREMELY* naive; in reality, you'll need
        # to do much more complex handling to ensure that arbitrary
        # objects -- such as Django model instances or querysets
        # -- can be serialized as JSON.
        def handledefault(o):
            if hasattr(o, "to_json"):
                return o.to_json()
            elif hasattr(o, "__dict__"):
                return o.__dict__
            else:
                raise ValueError("Not JSON serializable. Add to_json() or __dict__")
        content = json.dumps(self.get_context_data(**kwargs), default=handledefault)

        return HttpResponse(content, content_type='application/json')
