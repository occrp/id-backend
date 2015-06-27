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

# -- PROJECT SERIALIZERS
#
#
class ProjectSerializer(serializers.ModelSerializer):
    coordinator = UserField(queryset=get_user_model().objects.all())
    users = UserField(many=True, queryset=get_user_model().objects.all())

    class Meta:
        model = Project
        fields = ('id', 'title', 'coordinator', 'users')
