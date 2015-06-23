from podaci import PodaciView
from podaci.models import PodaciTag, PodaciFile

class Home(PodaciView):
    template_name = "podaci/home.jinja"

    def get_context_data(self):
        self.clear_breadcrumbs()
        num_displayed = 40
        tags = PodaciTag.objects.filter(allowed_users_read=self.request.user, parents=None)
        files = PodaciFile.objects.filter(allowed_users_read=self.request.user, tags=None)
        return {
            "num_files_displayed": files.count(),
            "num_tags": tags.count(),
            "num_files": files.count(),
            "result_tags": tags,
            "result_files": files,
        }


class Help(PodaciView):
    template_name = "podaci/help.jinja"


class Status(PodaciView):
    template_name = "podaci/status.jinja"

    def get_context_data(self):
        pass

class Statistics(PodaciView):
    template_name = "podaci/statistics.jinja"

    def get_context_data(self):
        pass
