import rules

from projects.models import Project, ProjectPlan, Story, StoryVersion, StoryTranslation

def get_story_from_lower_model(instance):
    if isinstance(instance, Story):
        return instance

    if isinstance(instance, StoryVersion):
        return instance.story

    if isinstance(instance, StoryTranslation):
        return instance.version.story
