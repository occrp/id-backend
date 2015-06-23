from podaci import PodaciView
from podaci.models import PodaciFile

class Search(PodaciView):
    template_name = "podaci/search.jinja"

    def get_context_data(self, **kwargs):
        return []


class SearchMention(PodaciView):
    template_name = None

    def get_context_data(self, **kwargs):
        # FIXME: This isn't very good
        query = self.request.GET.get("q")
        if query:
            return PodaciFile.objects.filter(name__contains=query)
        return []
