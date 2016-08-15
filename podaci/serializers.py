from .models import PodaciFile, PodaciTag, PodaciCollection
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers

from accounts.models import Profile


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


class ProfileField(serializers.RelatedField):

    def to_representation(self, user):
        return {'id': user.id, 'display_name': user.display_name}

    def to_internal_value(self, data):
        if isinstance(data, dict):
            data = data.get('id')
        return Profile.objects.get(pk=data)


class FileSerializer(serializers.ModelSerializer):
    title = serializers.CharField(allow_null=True, allow_blank=True)
    tags = TagField(many=True, read_only=False, allow_empty=True,
                    queryset=PodaciTag.objects.filter())
    allowed_users_read = ProfileField(many=True, read_only=False,
                                      allow_empty=True,
                                      queryset=Profile.objects.filter())
    allowed_users_write = ProfileField(many=True, read_only=False,
                                       allow_empty=True,
                                       queryset=Profile.objects.filter())
    created_by = ProfileField(read_only=True, allow_empty=False)

    class Meta:
        model = PodaciFile
        depth = 0
        fields = ('id', 'title', 'date_added', 'created_by',
                  'filename', 'url', 'sha256', 'size', 'mimetype',
                  'description', 'tags', 'collections', 'thumbnail',
                  'public_read', 'staff_read', 'allowed_users_read',
                  'allowed_users_write')
        read_only_fields = ('sha256', 'url', 'filename', 'created_by',
                            'date_added', 'thumbnail')

    def update(self, instance, data):
        instance.title = data.get('title')
        instance.public_read = data.get('public_read')
        instance.staff_read = data.get('staff_read')
        instance.description = data.get('description')
        instance.tags.clear()
        for tag in data.get('tags', []):
            instance.tags.add(tag)
        instance.allowed_users_read.clear()
        for user in data.get('allowed_users_read', []):
            instance.allowed_users_read.add(user)
        instance.allowed_users_write.clear()
        for user in data.get('allowed_users_write', []):
            instance.allowed_users_write.add(user)
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
