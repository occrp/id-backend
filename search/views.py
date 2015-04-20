from django.shortcuts import render
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import TemplateView, UpdateView, FormView

from search.api import ImageSearch, ImageSearchResult


class ImageSearch(TemplateView):
    template_name = "search/imagesearch.html"

    def get_context_data(self):
        s = ImageSearch()
        results = s.search(lat, lon, radius, startdate, enddate)

