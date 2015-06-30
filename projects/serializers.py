from django.contrib.auth import get_user_model

from rest_framework import serializers

from projects.models import *

# -- USER SERIALIZERS/FIELDS
#
#
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ('id', 'email', 'first_name', 'last_name')

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
        representation = {'id': value.id,
                          'email': value.email,
                          'first_name': value.first_name,
                          'last_name': value.last_name}
        return representation

# -- PROJECT SERIALIZERS/FIELDS/VALIDATORS
#
#

class ProjectSerializer(serializers.ModelSerializer):
    description = serializers.CharField(max_length=250, allow_null=True, allow_blank=True, required=False)
    coordinator = UserField(queryset=get_user_model().objects.all())
    users = UserField(many=True, queryset=get_user_model().objects.all())

    class Meta:
        model = Project
        fields = ('id', 'title', 'description', 'coordinator', 'users')

# -- STORY SERIALIZERS
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
    published = serializers.DateField(allow_null=True, required=False)
    podaci_root = serializers.CharField(max_length=50, read_only=True, required=False)

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
                  'podaci_root')
