#coding:utf-8
from django.shortcuts import render
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import TemplateView, View

from id.forms import CombinedSearchForm
from settings.settings import DEFAULTS
import logging
import traceback

from datetime import datetime
from search.models import SearchRequest
from core.mixins import JSONResponseMixin
from core.utils import json_dumps


class ImageSearchTemplate(TemplateView):
    template_name="search/search_images.jinja"
    def get_context_data(self):
        return { 'search_providers':SearchRequest().list_providers('image') }

class DocumentSearchTemplate(TemplateView):
    template_name = "search/search_documents.jinja"
    def get_context_data(self):
        return { 'form': CombinedSearchForm(initial=self.request.GET),
                 'search_providers':SearchRequest().list_providers('document') }

class SearchImageQuery(View, JSONResponseMixin):
    def get_context_data(self):
        query = {}
        query["q"] = self.request.GET.get("q", "")
        query["lat"] = float(self.request.GET.get("lat", 0.0))
        query["lon"] = float(self.request.GET.get("lon", 0.0))
        query["radius"] = int(self.request.GET.get("radius", 5000))
        query["startdate"] = self.request.GET.get("startdate", None)
        if query["startdate"]:
            query["startdate"] += "T" + self.request.GET.get("starttime", "00:00")
            print "Starting: " + query["startdate"]
        query["enddate"] = self.request.GET.get("enddate", None)
        if query["enddate"]:
            query["enddate"] += "T" + self.request.GET.get("endtime", "23:59")
            print "Ending: " + query["enddate"]
        query["offset"] = self.request.GET.get("offset", 0)
        query["count"] = self.request.GET.get("count", 100)

        chosen_providers = self.request.GET.getlist("search_providers[]", None)

        search = SearchRequest()
        search.requester = self.request.user
        search.search_type = 'image'
        search.query = json_dumps(query)
        search.save()
        return search.initiate_search(chosen_providers)


class SearchSocialQuery(View, JSONResponseMixin):
    def get_context_data(self):
        query = {}
        query["q"] = self.request.GET.get("q", "")

        chosen_providers = self.request.GET.getlist("providers[]", None)

        search = SearchRequest()
        search.requester = self.request.user
        search.search_type = 'social'
        search.query = json_dumps(query)
        search.save()
        return search.initiate_search(chosen_providers)

        return {
            "status": True
        }


class SearchCheck(View, JSONResponseMixin):
    def get_context_data(self):
        searchid = self.request.GET.get("id", 0)
        if not searchid:
            return {"status": False, "error": "Must supply valid ID"}
        search = SearchRequest.objects.get(id=searchid)
        return {
            "status": True,
            "done": search.is_done(), 
            "bots_total": search.bots_done(),
            "bots_done": search.bots_done(),
            "results": search.get_results(),
            "checkin_after": -1 if search.is_done() else 500,
        }


def search(providers, query, offset, limit):
    #if not all([provider in DEFAULTS['search']['provider_classes'] for provider in providers]):
    #    raise ValueError("Unknown provider in provider list: %s" % providers)

    providers = [x for x in searchproviders.SEARCH_PROVIDERS if x.provider_id in providers]
    results = []
    messages = []
    for handler_class in providers:
        try:
            handler = handler_class()
            handler.search(query=query, offset=offset, limit=limit)
            results.append(handler.results)
        except Exception:
            messages.append('We could not retrieve results from %s.'
                             'Please try again in a few minutes' %
                             handler_class)
            logging.error('search handler %s failed: %s' % (
                handler_class.result_type,
                traceback.format_exc()))

    return results, messages

class DocumentSearchQuery(View, JSONResponseMixin):
    def get_context_data(self):
        query = {}
        query["q"] = self.request.GET.get("q", "")
        query["startdate"] = self.request.GET.get("startdate", None)
        if query["startdate"]:
            query["startdate"] += "T" + self.request.GET.get("starttime", "00:00")
            print "Starting: " + query["startdate"]
        query["enddate"] = self.request.GET.get("enddate", None)
        if query["enddate"]:
            query["enddate"] += "T" + self.request.GET.get("endtime", "23:59")
            print "Ending: " + query["enddate"]
        query["offset"] = self.request.GET.get("offset", 0)
        query["count"] = self.request.GET.get("count", 100)

        chosen_providers = self.request.GET.getlist("search_providers[]", None)

        search = SearchRequest()
        search.requester = self.request.user
        search.search_type = 'document'
        search.query = json_dumps(query)
        search.save()
        return search.initiate_search(chosen_providers)

class CombinedSearchHandler(TemplateView):
    template_name = "search/search_combined.jinja"

    def get_context_data(self, **kwargs):
        context = super(CombinedSearchHandler, self).get_context_data(**kwargs)
        print self.request.POST
        print "GET: %s" % (self.request.GET,)
        print "POST: %s" % (self.request.POST,)
        form = CombinedSearchForm(initial=self.request.GET)
        print "Form data: %s" % (form.data)
        #if not form.is_valid():
        #form = CombinedSearchForm()

        results = []
        messages = []
        if 'query' in self.request.GET:
            context["query_made"] = True
            providers = self.request.GET.getlist("search_providers")
            query = self.request.GET.get("query")
            results, messages = search(providers, query, 0, 10)

        result_count = len(results)

        context["form"] = form
        context["start"] = int(form["offset"].value()) + 1
        context["end"] = int(form["offset"].value()) + int(form["limit"].value())
        context["results"] = results
        context["result_count"] = result_count
        context["messages"] = messages
        context["query"] = self.request.POST.get("query", "")
        return context
