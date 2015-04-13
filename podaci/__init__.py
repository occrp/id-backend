from django.http import HttpResponse
from django.views.generic import TemplateView
#from django.contrib.auth.models import User
from django.contrib.auth import get_user_model # as per https://docs.djangoproject.com/en/dev/topics/auth/customizing/#referencing-the-user-model
from core.mixins import JSONResponseMixin
from core.auth import require_staff
from podaci.filesystem import *
import json
from settings.settings import PODACI_SERVERS, PODACI_ES_INDEX, PODACI_FS_ROOT

class PodaciMixin:
    def breadcrumb_push(self, id):
        if not self.request.session.get("breadcrumbs", False):
            self.request.session["breadcrumbs"] = []
        self.request.session["breadcrumbs"].append(id)

    def breadcrumb_pop(self):
        self.request.session["breadcrumbs"].pop()

    def breadcrumb_exists(self, id):
        if not self.request.session.get("breadcrumbs", False):
            self.request.session["breadcrumbs"] = []
        return id in self.request.session["breadcrumbs"]

    def breadcrumb_index(self, id):
        if not self.request.session.get("breadcrumbs", False):
            self.request.session["breadcrumbs"] = []
        return self.request.session["breadcrumbs"].index(id)

    def get_breadcrumbs(self):
        return [Tag(self.fs, bc) for bc in self.request.session.get("breadcrumbs", [])]

    def clear_breadcrumbs(self):
        self.request.session["breadcrumbs"] = []

    def podaci_setup(self):
        self.fs = FileSystem(
            PODACI_SERVERS, PODACI_ES_INDEX, 
            PODACI_FS_ROOT, self.request.user)


class PodaciView(TemplateView, PodaciMixin, JSONResponseMixin):
    def dispatch(self, *args, **kwargs):
        # All of podaci is for staff only.
        require_staff(self.request.user)
        self.podaci_setup()
        return super(PodaciView, self).dispatch(*args, **kwargs)

    def post(self, request, **kwargs):
        return self.json_response(**kwargs)

    def get(self, request, **kwargs):
        format = request.GET.get("format", "html")
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
