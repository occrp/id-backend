from django.views.generic import TemplateView
from id.forms import CombinedSearchForm
from settings.settings import DEFAULTS
import searchproviders
import logging
import traceback


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


class CombinedSearchHandler(TemplateView):
    template_name = "search/search_combined.html"

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
