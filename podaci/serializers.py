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
    thumbnail = serializers.CharField(read_only=True)
    class Meta:
        model = PodaciFile
        # depth = 1
        fields = ('id', 'name', 'title', 'date_added', 'created_by', 'filename', 'url', 'sha256', 'size', 'mimetype', 'description', 'tags', 'collections', 'thumbnail', 'public_read', 'staff_read')

class CollectionSerializer(serializers.ModelSerializer):
    # FIXME: This needs to be unhidden before Sharing is implemented
    owner = serializers.HiddenField(default=serializers.CurrentUserDefault())
    class Meta:
        model = PodaciCollection
        # depth = 1
        fields = ('id', 'name', 'description', 'owner', 'files', 'shared_with')
