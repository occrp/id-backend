from django.db.models import Q

from projects.models import Project, Story

def user_in_story_filter(story_objects, user):
        return story_objects.filter(Q(reporters__in=[user]) |
                                    Q(researchers__in=[user]) |
                                    Q(editors__in=[user]) |
                                    Q(copy_editors__in=[user]) |
                                    Q(fact_checkers__in=[user]) |
                                    Q(translators__in=[user]) |
                                    Q(artists__in=[user])).distinct()

def user_in_story_or_project_filter(story_objects, user):
        return story_objects.filter(Q(reporters__in=[user]) |
                                    Q(researchers__in=[user]) |
                                    Q(editors__in=[user]) |
                                    Q(copy_editors__in=[user]) |
                                    Q(fact_checkers__in=[user]) |
                                    Q(translators__in=[user]) |
                                    Q(artists__in=[user]) |
                                    Q(project__coordinators=user) |
                                    Q(project__users__in=[user])).distinct()

def user_in_story_or_project_from_story_version_filter(story_version_objects, user):
    return story_version_objects.filter(Q(story__reporters__in=[user]) |
                                        Q(story__researchers__in=[user]) |
                                        Q(story__editors__in=[user]) |
                                        Q(story__copy_editors__in=[user]) |
                                        Q(story__fact_checkers__in=[user]) |
                                        Q(story__translators__in=[user]) |
                                        Q(story__artists__in=[user]) |
                                        Q(story__project__coordinators=user) |
                                        Q(story__project__users__in=[user])).distinct()
