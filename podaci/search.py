from podaci import PodaciView

class Search(PodaciView):
    template_name = "podaci/search.jinja"

    def get_context_data(self, **kwargs):
        return []


class SearchMention(PodaciView):
    template_name = None

    def get_context_data(self, **kwargs):
        query = self.request.GET.get("q", None)
        return self.fs.search_all_by_name(query)
