#coding:utf-8
from django.shortcuts import render
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import TemplateView, UpdateView, FormView

from datetime import datetime
from search.api import ImageSearchDispatcher, ImageSearchResult


class ImageSearch(TemplateView):
    template_name = "search/search_images.jinja"

    def get_context_data(self):
        res = {"results": []}
        res["q"] = q = self.request.GET.get("q", "").encode("utf-8")
        if q:
            res["lat"] = lat = self.request.GET.get("lat")
            res["lon"] = lon = self.request.GET.get("lon")
            res["radius"] = radius = int(self.request.GET.get("radius", 5000))
            res["startdate"] = startdate = self.request.GET.get("startdate", None)
            res["enddate"] = enddate = self.request.GET.get("enddate", None)
            res["offset"] = offset = self.request.GET.get("offset", 0)
            res["count"] = count = self.request.GET.get("count", 100)
            s = ImageSearchDispatcher()
            res["results"] = s.search(q, lat, lon, radius, startdate, enddate, offset, count)
            return res

        return res