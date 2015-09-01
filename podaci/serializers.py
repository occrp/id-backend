from podaci.models import PodaciFile, PodaciTag, PodaciCollection
from rest_framework import serializers
from id.models import Profile


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ('id', 'email')


class TagSerializer(serializers.ModelSerializer):
    # we need files
    # but only those that the user has access to
    # files = UserField(many=True, queryset=PodaciFile.objects.filter())

    class Meta:
        model = PodaciTag
        fields = ('id', 'name', 'icon', 'files')


class FileSerializer(serializers.ModelSerializer):
    thumbnail = serializers.CharField(read_only=True)
    # created_by = ProfileSerializer()

    class Meta:
        model = PodaciFile
        depth = 0
        fields = ('id', 'name', 'title', 'date_added', 'created_by',
                  'filename', 'url', 'sha256', 'size', 'mimetype',
                  'description', 'tags', 'collections', 'thumbnail',
                  'public_read', 'staff_read')


class CollectionSerializer(serializers.ModelSerializer):
    # FIXME: This needs to be unhidden before Sharing is implemented
    owner = serializers.HiddenField(default=serializers.CurrentUserDefault())
    # owner = ProfileSerializer()

    class Meta:
        model = PodaciCollection
        depth = 0
        fields = ('id', 'name', 'description', 'files', 'owner', 'shared_with')
        extra_kwargs = {
            'files': {'allow_empty': True},
            'shared_with': {'allow_empty': True}
        }
