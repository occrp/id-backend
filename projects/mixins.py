from django.db.models import Q
from projects.models import Project, Story

class ProjectQuerySetMixin(object):
    def get_queryset(self):
        if self.request.user.is_superuser:
            return Project.objects.all()
        else:
            return Project.objects.filter(coordinator=self.request.user)

class StoryQuerySetBaseMixin(object):
    def user_in_story_filter(self, story_objects, user):
        return story_objects.filter(Q(reporters__in=[user]) |
                                    Q(researchers__in=[user]) |
                                    Q(editors__in=[user]) |
                                    Q(copy_editors__in=[user]) |
                                    Q(fact_checkers__in=[user]) |
                                    Q(translators__in=[user]) |
                                    Q(artists__in=[user]) |
                                    Q(project__coordinator=user))

class StoryQuerySetMixin(StoryQuerySetBaseMixin):
    def get_queryset(self):
        if self.request.user.is_superuser:
            stories = Story.objects.all()
        else:
            stories = self.user_in_story_filter(Story.objects.all(), self.request.user)

        return stories

class StoryListQuerySetMixin(StoryQuerySetMixin):
    def get_queryset(self, project_id):
        stories = super(StoryListQuerySetMixin, self).get_queryset()
        return stories.filter(project__id=project_id)

# class StoryVersionQuerySet(object):