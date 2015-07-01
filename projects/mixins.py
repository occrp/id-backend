from django.db.models import Q
from projects.models import Project, Story

class ProjectQuerySetMixin:
    def get_queryset(self):
        if self.request.user.is_superuser:
            return Project.objects.all()
        else:
            return Project.objects.filter(coordinator=self.request.user)


class StoryQuerySetMixin:
    def get_queryset(self, project_id=0):
        if self.request.user.is_superuser:
            stories = Story.objects.all()
        else:
            stories = Story.objects.filter(Q(reporters__in=[self.request.user]) |
                                           Q(researchers__in=[self.request.user]) |
                                           Q(editors__in=[self.request.user]) |
                                           Q(copy_editors__in=[self.request.user]) |
                                           Q(fact_checkers__in=[self.request.user]) |
                                           Q(translators__in=[self.request.user]) |
                                           Q(artists__in=[self.request.user]) |
                                           Q(project__coordinator=self.request.user))

        if project_id > 0:
            stories.filter(project__id=project_id)

        return stories
