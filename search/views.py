# coding:utf-8
from django.views.generic import TemplateView, View

from search.forms import CombinedSearchForm
import logging

from search.models import SearchRequest
from core.mixins import JSONResponseMixin

log = logging.getLogger(__name__)


class ImageSearchTemplate(TemplateView):
    template_name = "search/search_images.jinja"

    def get_context_data(self):
        return {
            'search_providers': SearchRequest.by_type('image')
        }


class DocumentSearchTemplate(TemplateView):
    template_name = "search/search_documents.jinja"

    def get_context_data(self):
        return {
            'form': CombinedSearchForm(initial=self.request.GET),
            'search_providers': SearchRequest.by_type('document')
        }


class SearchImageQuery(View, JSONResponseMixin):
    def get_context_data(self):
        query = {}
        query["q"] = self.request.GET.get("q", "")
        try:
            query["lat"] = float(self.request.GET.get("lat"))
        except (ValueError, TypeError):
            query["lat"] = None
        try:
            query["lon"] = float(self.request.GET.get("lon"))
        except (ValueError, TypeError):
            query["lon"] = None
        try:
            query["radius"] = int(self.request.GET.get("radius"))
        except (ValueError, TypeError):
            query["radius"] = 5000
        query["startdate"] = self.request.GET.get("startdate", None)
        if query["startdate"]:
            query["startdate"] += "T" + self.request.GET.get("starttime", "00:00")
            print "Starting: " + query["startdate"]
        query["enddate"] = self.request.GET.get("enddate", None)
        if query["enddate"]:
            query["enddate"] += "T" + self.request.GET.get("endtime", "23:59")
            print "Ending: " + query["enddate"]
        query["offset"] = self.request.GET.get("offset", 0)
        query["count"] = self.request.GET.get("count", 25)

        provider = self.request.GET.get("provider")
        return SearchRequest.construct(query, provider, self.request.user,
                                       'image')


class SearchSocialQuery(View, JSONResponseMixin):
    def get_context_data(self):
        query = {}
        query["q"] = self.request.GET.get("q", "")

        provider = self.request.GET.get("provider")
        return SearchRequest.construct(query, provider, self.request.user,
                                       'social')


class DocumentSearchQuery(View, JSONResponseMixin):

    def get_context_data(self):
        query = {}
        query["q"] = self.request.GET.get("q", "")
        query["startdate"] = self.request.GET.get("startdate", None)
        if query["startdate"]:
            query["startdate"] += "T" + self.request.GET.get("starttime", "00:00")
        query["enddate"] = self.request.GET.get("enddate", None)
        if query["enddate"]:
            query["enddate"] += "T" + self.request.GET.get("endtime", "23:59")
        query["offset"] = self.request.GET.get("offset", 0)
        query["count"] = self.request.GET.get("count", 100)

        provider = self.request.GET.get("provider")
        return SearchRequest.construct(query, provider, self.request.user,
                                       'document')
