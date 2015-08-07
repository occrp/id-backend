from podaci.models import PodaciFile, PodaciTag, PodaciCollection
from rest_framework import serializers

class TagSerializer(serializers.ModelSerializer):
    # we need files
    # but only those that the user has access to
    files = UserField(many=True, queryset=PodaciFile.objects.filter())
    
    class Meta:
        model = PodaciTag
        fields = ('id', 'name', 'icon', 'files')

class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = PodaciFile
        fields = ('id', 'name', 'title', 'date_added', 'created_by', 'filename',
                  'url', 'sha256', 'size', 'mimetype', 'description', 'tags', 'collections')

class CollectionSerializer(serializers.ModelSerializer):
    # we need files
    # but only those that the user has access to
    class Meta:
        model = PodaciCollection
        fields = ('id', 'name', 'description', 'owner', 'files')
