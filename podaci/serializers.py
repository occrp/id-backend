from podaci.models import PodaciFile, PodaciTag, PodaciCollection
from rest_framework import serializers

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = PodaciTag
        fields = ('id', 'name', 'icon', 'files')

class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = PodaciFile
        fields = ('id', 'name', 'title', 'date_added', 'created_by', 'filename', 'url', 'sha256', 'size', 'mimetype', 'description', 'tags', 'collections')

class CollectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PodaciCollection
        fields = ('id', 'name', 'description', 'owner', 'files')
