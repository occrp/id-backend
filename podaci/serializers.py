from podaci.models import PodaciFile, PodaciTag, PodaciCollection
from django.core.exceptions import ObjectDoesNotExist
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


class TagField(serializers.RelatedField):

    def to_representation(self, tag):
        return tag.name

    def to_internal_value(self, name):
        try:
            return PodaciTag.objects.get(name=name)
        except ObjectDoesNotExist:
            t = PodaciTag.objects.create(name=name)
            t.save()
            return t


class FileSerializer(serializers.ModelSerializer):
    title = serializers.CharField(allow_null=True, allow_blank=True)
    tags = TagField(many=True, read_only=False, allow_empty=True,
                    queryset=PodaciTag.objects.filter())

    class Meta:
        model = PodaciFile
        depth = 0
        fields = ('id', 'title', 'date_added', 'created_by',
                  'filename', 'url', 'sha256', 'size', 'mimetype',
                  'description', 'tags', 'collections', 'thumbnail',
                  'public_read', 'staff_read')
        read_only_fields = ('sha256', 'url', 'filename', 'created_by',
                            'date_added', 'thumbnail')

    def update(self, instance, data):
        instance.title = data.get('title')
        instance.description = data.get('description')
        instance.tags.clear()
        for tag in data.get('tags', []):
            instance.tags.add(tag)
        instance.update()
        return instance


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
