from django.db.models import Q
from projects.models import Project, Story

class ProjectQuerySetMixin:
    def get_queryset(self):
        if self.request.user.is_superuser:
            return Project.objects.all()
        else:
            return Project.objects.filter(coordinator=self.request.user)


class StoryQuerySetMixin:
    def get_queryset(self):
        if self.request.user.is_superuser:
            print "apparently i am  super user!"
            stories = Story.objects.all()
        else:
            print "im not a super user!!!"
            stories = Story.objects.filter(Q(reporters__in=[self.request.user]) |
                                           Q(researchers__in=[self.request.user]) |
                                           Q(editors__in=[self.request.user]) |
                                           Q(copy_editors__in=[self.request.user]) |
                                           Q(fact_checkers__in=[self.request.user]) |
                                           Q(translators__in=[self.request.user]) |
                                           Q(artists__in=[self.request.user]) |
                                           Q(project__coordinator=self.request.user))

        if 'project_id' in self.kwargs:
            stories.objects.filter(project__id=int(self.kwargs['project_id']))

        return stories
