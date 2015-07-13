from django.contrib.auth import get_user_model

from rest_framework import serializers

from projects.models import Project, Story, StoryVersion, StoryTranslation, ProjectPlan

# -- USER SERIALIZERS/FIELDS
#
#
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ('id', 'display_name', 'email', 'first_name', 'last_name')

class UserField(serializers.RelatedField):

    def to_internal_value(self, value):
        try:
            user_id = int(value)
        except ValueError:
            raise serializers.ValidationError('id must be an integer and correspond to an existing user')

        try:
            user = get_user_model().objects.get(id=user_id)
        except get_user_model().DoesNotExist:
            raise serializers.ValidationError('user does not exist')

        return user

    def to_representation(self, value):
        representation = UserSerializer(value)
        return representation.data

# -- PROJECT SERIALIZERS/FIELDS/VALIDATORS
#
#

class ProjectSerializer(serializers.ModelSerializer):
    description = serializers.CharField(max_length=250, allow_null=True, allow_blank=True, required=False)
    coordinators = UserField(many=True, queryset=get_user_model().objects.all())
    users = UserField(many=True, queryset=get_user_model().objects.all(), required=False)
    story_count = serializers.IntegerField(source='stories.count', read_only=True)

    class Meta:
        model = Project
        fields = ('id', 'title', 'description', 'coordinators', 'users', 'story_count')

# -- STORY SERIALIZERS/FIELS
#
#
class StorySerializer(serializers.ModelSerializer):
    project = serializers.PrimaryKeyRelatedField(queryset=Project.objects.all())
    thesis = serializers.CharField(max_length=500, allow_null=True, allow_blank=True, required=False)
    reporters = UserField(many=True, queryset=get_user_model().objects.all())
    researchers = UserField(many=True, queryset=get_user_model().objects.all())
    editors = UserField(many=True, queryset=get_user_model().objects.all())
    copy_editors = UserField(many=True, queryset=get_user_model().objects.all())
    fact_checkers = UserField(many=True, queryset=get_user_model().objects.all())
    translators = UserField(many=True, queryset=get_user_model().objects.all())
    artists = UserField(many=True, queryset=get_user_model().objects.all())
    published = serializers.DateTimeField(allow_null=True, required=False)
    podaci_root = serializers.CharField(max_length=50, read_only=True, required=False)
    version_count = serializers.IntegerField(source='versions.count', read_only=True)

    class Meta:
        model = Story
        fields = ('id',
                  'project',
                  'title',
                  'thesis',
                  'reporters',
                  'researchers',
                  'editors',
                  'copy_editors',
                  'fact_checkers',
                  'translators',
                  'artists',
                  'published',
                  'podaci_root',
                  'version_count')

class StoryField(serializers.RelatedField):

    def to_internal_value(self, value):
        try:
            story_id = int(value)
        except ValueError:
            raise serializers.ValidationError('id must be an integer and correspond to an existing story')

        try:
            story = Story.objects.get(id=story_id)
        except Story.DoesNotExist:
            raise serializers.ValidationError('story does not exist')

        return story

    def to_representation(self, value):
        representation = {'id': value.id,
                          'title': value.title,
                          'thesis': value.thesis,
                          'published': value.published,
                          'podaci_root': value.podaci_root}
        return representation

# -- STORY VERSION SERIALIZERS
#
#
class StoryVersionSerializer(serializers.ModelSerializer):
    story = serializers.PrimaryKeyRelatedField(queryset=Story.objects.all())
    author = UserField(queryset=get_user_model().objects.all())

    class Meta:
        model = StoryVersion
        fields = ('id',
                  'story',
                  'timestamp',
                  'author',
                  'title',
                  'text')


# -- STORY TRANSLATION SERIALIZERS
#
#
class StoryTranslationSerializer(serializers.ModelSerializer):
    version = serializers.PrimaryKeyRelatedField(queryset=StoryVersion.objects.all())
    translator = UserField(queryset=get_user_model().objects.all())

    class Meta:
        model = StoryTranslation
        fields = ('id',
                  'version',
                  'language_code',
                  'timestamp',
                  'translator',
                  'verified',
                  'live',
                  'title',
                  'text')


# -- PROJECT PLAN SERIALIZERS
#
#
class ProjectPlanSerializer(serializers.ModelSerializer):
    project = serializers.PrimaryKeyRelatedField(queryset=Project.objects.all())
    responsible_users = UserField(many=True, queryset=get_user_model().objects.all())
    related_stories = StoryField(many=True, queryset=Story.objects.all())

    class Meta:
        model = ProjectPlan
        fields = ('id',
                  'project',
                  'start_date',
                  'end_date',
                  'title',
                  'description',
                  'responsible_users',
                  'related_stories',
                  'order')
