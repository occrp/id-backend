from podaci import PodaciView
from podaci.models import PodaciTag, PodaciFile
from django.db.models import Q

class Home(PodaciView):
    template_name = "podaci/home.jinja"

    def get_context_data(self):
        self.clear_breadcrumbs()
        num_displayed = 40
        tagterms = Q(allowed_users_read=self.request.user)
        if self.request.user.is_staff:
            tagterms |= Q(staff_read=True)
            stafftags = PodaciTag.objects.filter(staff_read=True)
        else:
            stafftags = []
        tags = PodaciTag.objects.filter(parents=None).filter(tagterms)
        publictags = PodaciTag.objects.filter(public_read=True)
        files = PodaciFile.objects.filter(allowed_users_read=self.request.user, tags=None)
        return {
            "piles": tags,
            "files": files,
            "public_piles": publictags,
            "staff_piles": stafftags,
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
