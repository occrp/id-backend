from django.http import HttpResponse
from django.views.generic import TemplateView
#from django.contrib.auth.models import User
from django.contrib.auth import get_user_model # as per https://docs.djangoproject.com/en/dev/topics/auth/customizing/#referencing-the-user-model
from core.mixins import JSONResponseMixin
from core.auth import require_staff
from core.utils import json_dumps
import json
from settings.settings import PODACI_SERVERS, PODACI_ES_INDEX, PODACI_FS_ROOT
from podaci.models import PodaciTag, PodaciFile

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
        return [PodaciTag(self.fs, bc) for bc in self.request.session.get("breadcrumbs", [])]

    def clear_breadcrumbs(self):
        self.request.session["breadcrumbs"] = []

    #def podaci_setup(self):
    #    self.fs = FileSystem(
    #        PODACI_SERVERS, PODACI_ES_INDEX, 
    #        PODACI_FS_ROOT, self.request.user)


class PodaciView(TemplateView, PodaciMixin, JSONResponseMixin):
    def dispatch(self, *args, **kwargs):
        # All of podaci is for staff only.
        require_staff(self.request.user)
        # self.podaci_setup()
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
        content = json_dumps(self.get_context_data(**kwargs))
        return HttpResponse(content, content_type='application/json')
