from django.shortcuts import render
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import TemplateView, UpdateView, FormView

from datetime import datetime
from search.api import ImageSearchDispatcher, ImageSearchResult


class ImageSearch(TemplateView):
    template_name = "search/search_images.jinja"

    def get_context_data(self):
        q = self.request.GET.get("q", None).encode("utf-8")
        if q:
            lat = self.request.GET.get("lat")
            lon = self.request.GET.get("lon")
            radius = int(self.request.GET.get("radius", 5000))
            startdate = self.request.GET.get("startdate", None)
            enddate = self.request.GET.get("enddate", None)
            offset = self.request.GET.get("offset", 0)
            count = self.request.GET.get("count", 100)
            s = ImageSearchDispatcher()
            results = s.search(q, lat, lon, radius, startdate, enddate, offset, count)
            return {"results": results}

        return {"results": []}
