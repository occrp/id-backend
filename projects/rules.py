from __future__ import absolute_import

import rules

from projects.models import Project, ProjectPlan, Story, StoryVersion, StoryTranslation

@rules.predicate(bind=True)
def is_project_coordinator(self, user, instance):
    project = find_project_in_context_or_get(self, instance)

    if user in project.coordinators.all():
        return True

    return False

@rules.predicate(bind=True)
def is_project_member(self, user, instance):
    project = find_project_in_context_or_get(self, instance)

    if user in project.users.all():
        return True

    return False

# -- HELPERS
#
#
@rules.predicate
def is_superuser(user, instance):
    if user.is_superuser:
        return True

    return False

def find_project_in_context_or_get(predicate, instance):
    project = predicate.context.get('project')
    if project is not None:
        return project

    project = traverse_to_project(instance)
    predicate.context['project'] = project
    return project

def traverse_to_project(instance):
    if isinstance(instance, Project):
        return instance

    if isinstance(instance, Story):
        return instance.project

    if isinstance(instance, StoryVersion):
        return instance.story.project

    if isinstance(instance, StoryTranslation):
        return instance.version.story.project

def travese_to_story(instance):
    if isinstance(instance, Story):
        return instance

    if isinstance(instance, StoryVersion):
        return instance.story

    if isinstance(instance, StoryTranslation):
        return instance.version.story

# -- SETUP THE RULES
#
#
rules.add_perm('projects.can_alter_or_delete_project', is_project_coordinator | is_superuser)
rules.add_perm('projects.can_view_project', is_project_member | is_superuser)
