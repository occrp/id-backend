from podaci.models import PodaciFile, PodaciTag
from rest_framework import serializers

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = PodaciTag

class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = PodaciTag
