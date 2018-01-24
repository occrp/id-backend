import os.path

from django.urls import reverse
from filetype import guess_mime
from rest_framework_json_api import serializers

from api_v3.models import Attachment


class AttachmentFileField(serializers.FileField):

    def to_representation(self, obj):
        if obj.instance.upload and self.context.get('request', None):
            return self.context['request'].build_absolute_uri(
                reverse('download-detail', args=[obj.instance.id])
            )


class AttachmentSerializer(serializers.ModelSerializer):

    included_serializers = {
        'user': 'api_v3.serializers.ProfileSerializer',
        'ticket': 'api_v3.serializers.TicketSerializer'
    }

    file_name = serializers.SerializerMethodField()
    file_size = serializers.SerializerMethodField()
    mime_type = serializers.SerializerMethodField()
    upload = AttachmentFileField()

    class Meta:
        model = Attachment
        read_only_fields = ('user',)
        fields = (
            'id',
            'user',
            'ticket',
            'upload',
            'file_name',
            'file_size',
            'mime_type',
            'created_at'
        )

    def get_file_name(self, obj):
        if obj.upload:
            return os.path.basename(obj.upload.name)

    def get_file_size(self, obj):
        if obj.upload and os.path.exists(obj.upload.path):
            return obj.upload.size
        return 0

    def get_mime_type(self, obj):
        if obj.upload and os.path.exists(obj.upload.path):
            try:
                return guess_mime(obj.upload.path)
            except TypeError:
                return 'application/octet-stream'
