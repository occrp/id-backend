from django.contrib.auth import get_user_model

from rest_framework import serializers

from projects.models import *

# -- SERIALIZERS
#
#
class ProjectSerializer(serializers.ModelSerializer):
    users = serializers.PrimaryKeyRelatedField(many=True, queryset=get_user_model().objects.all())

    class Meta:
        model = Project
        field = {'url', 'title', 'coordinator', 'users'}
