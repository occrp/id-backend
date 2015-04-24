#coding:utf-8
from django.shortcuts import render
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import TemplateView, View

from datetime import datetime
from search.models import SearchRequest
from core.mixins import JSONResponseMixin
from core.utils import json_dumps


class ImageSearchQuery(View, JSONResponseMixin):
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

        chosen_providers = self.request.GET.getlist("providers", None)

        search = SearchRequest()
        search.requester = self.request.user
        search.search_type = 'image'
        search.query = json_dumps(query)
        search.save()
        return search.initiate_search(chosen_providers)


class ImageSearchCheck(View, JSONResponseMixin):
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
