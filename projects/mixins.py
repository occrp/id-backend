from django.db.models import Q
from projects.models import Project, Story, StoryVersion, StoryTranslation

# -- PROJECT MIXINS
#
#
class ProjectMembershipMixin(object):
    def user_is_project_user(self, project_id, user):
        if user.is_superuser:
            return True

        result = Project.objects.all().filter(id=project_id) \
                 .filter(Q(coordinator=user) | Q(users__in=[user])).count()

        if result == 0:
            return False

        return True

class ProjectQuerySetMixin(object):
    def get_queryset(self):
        if self.request.user.is_superuser:
            return Project.objects.all()
        else:
            return Project.objects.filter(coordinator=self.request.user)

# -- STORY MIXINS
#
#
class StoryQuerySetBaseMixin(object):
    def user_in_story_filter(self, story_objects, user):
        return story_objects.filter(Q(reporters__in=[user]) |
                                    Q(researchers__in=[user]) |
                                    Q(editors__in=[user]) |
                                    Q(copy_editors__in=[user]) |
                                    Q(fact_checkers__in=[user]) |
                                    Q(translators__in=[user]) |
                                    Q(artists__in=[user]))

    def user_is_story_user(self, story_id, user):
        story = Story.objects.all().filter(id=story_id)
        result = self.user_in_story_filter(story, user).count()

        if result == 0:
            return False

        return True

    def user_in_story_or_project_filter(self, story_objects, user):
        return story_objects.filter(Q(reporters__in=[user]) |
                                    Q(researchers__in=[user]) |
                                    Q(editors__in=[user]) |
                                    Q(copy_editors__in=[user]) |
                                    Q(fact_checkers__in=[user]) |
                                    Q(translators__in=[user]) |
                                    Q(artists__in=[user]) |
                                    Q(project__coordinator=user) |
                                    Q(project__users__in=[user]))

    def user_is_story_or_project_user(self, story_id, user):
        story = Story.objects.all().filter(id=story_id)
        result = self.user_in_story_or_project_filter(story, user).count()

        if result == 0:
            return False

        return True

class StoryQuerySetMixin(StoryQuerySetBaseMixin):
    def get_queryset(self):
        if self.request.user.is_superuser:
            stories = Story.objects.all()
        else:
            stories = self.user_in_story_or_project_filter(Story.objects.all(), self.request.user)

        return stories

class StoryListQuerySetMixin(StoryQuerySetMixin):
    def get_queryset(self, project_id):
        stories = super(StoryListQuerySetMixin, self).get_queryset()
        return stories.filter(project__id=project_id)

# -- STORY VERSION MIXINS
#
#
class StoryVersionQuerySetMixin(StoryQuerySetBaseMixin):
    def get_queryset(self):
        if self.request.user.is_superuser:
            return StoryVersion.objects.all()
        else:
            story_versions = StoryVersion.objects.filter(Q(story__reporters__in=[self.request.user]) |
                                                         Q(story__researchers__in=[self.request.user]) |
                                                         Q(story__editors__in=[self.request.user]) |
                                                         Q(story__copy_editors__in=[self.request.user]) |
                                                         Q(story__fact_checkers__in=[self.request.user]) |
                                                         Q(story__translators__in=[self.request.user]) |
                                                         Q(story__artists__in=[self.request.user]) |
                                                         Q(story__project__coordinator=self.request.user) |
                                                         Q(story__project__users__in=[self.request.user]))

            return story_versions

class StoryVersionListQuerySetMixin(StoryVersionQuerySetMixin):
    def get_queryset(self, story_id):
        story_versions = super(StoryVersionListQuerySetMixin, self).get_queryset()
        return story_versions.filter(story__id=story_id)

# -- STORY TRANSLATION MIXINS
#
#
class StoryTranslationQuerySetMixin(StoryQuerySetBaseMixin):
    def user_is_story_user(self, version_id, user):
        try:
            story = StoryVersion.objects.get(id=version_id).story
            return super(StoryTranslationQuerySetMixin, self).user_is_story_user(story.id, user)
        except StoryVersion.DoesNotExist:
            return False

    def get_queryset(self):
        if self.request.user.is_superuser:
            return StoryTranslation.objects.all()
        else:
            story_translations = StoryTranslation.objects.filter(Q(translator=self.request.user) |
                                                                 Q(version__author=self.request.user) |
                                                                 Q(version__story__reporters__in=[self.request.user]) |
                                                                 Q(version__story__researchers__in=[self.request.user]) |
                                                                 Q(version__story__editors__in=[self.request.user]) |
                                                                 Q(version__story__copy_editors__in=[self.request.user]) |
                                                                 Q(version__story__fact_checkers__in=[self.request.user]) |
                                                                 Q(version__story__translators__in=[self.request.user]) |
                                                                 Q(version__story__artists__in=[self.request.user]) |
                                                                 Q(version__story__project__coordinator=self.request.user) |
                                                                 Q(version__story__project__users__in=[self.request.user]))
            return story_translations
