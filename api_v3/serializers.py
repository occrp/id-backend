import os.path

import magic
from rest_framework_json_api import serializers, relations
from rest_framework import fields

from .models import Profile, Ticket, Action, Attachment, Comment, Responder


class ProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = Profile
        read_only_fields = (
            'id',
            'email',
            'first_name',
            'last_name',
            'is_staff',
            'is_superuser',
            'locale'
        )
        fields = (
            'id',
            'email',
            'first_name',
            'last_name',
            'is_staff',
            'is_superuser',
            'settings',
            'locale'
        )


class ResponderSerializer(serializers.ModelSerializer):

    included_serializers = {
        'user': ProfileSerializer,
        'ticket': 'api_v3.serializers.TicketSerializer'
    }

    class Meta:
        model = Responder
        fields = ('ticket', 'user')
        resource_name = 'Responder'


class AttachmentSerializer(serializers.ModelSerializer):

    included_serializers = {
        'user': ProfileSerializer,
        'ticket': 'api_v3.serializers.TicketSerializer'
    }

    file_name = serializers.SerializerMethodField()
    file_size = serializers.SerializerMethodField()
    mime_type = serializers.SerializerMethodField()

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
        if obj.upload:
            return obj.upload.size
        return 0

    def get_mime_type(self, obj):
        if obj.upload:
            return magic.from_file(obj.upload.name, mime=True)


class CommentSerializer(serializers.ModelSerializer):

    included_serializers = {
        'user': ProfileSerializer,
        'ticket': 'api_v3.serializers.TicketSerializer'
    }

    class Meta:
        model = Comment
        read_only_fields = ('user',)
        fields = (
            'id',
            'user',
            'ticket',
            'body',
            'created_at'
        )


class TicketSerializer(serializers.ModelSerializer):

    included_serializers = {
        'users': ProfileSerializer,
        'requester': ProfileSerializer,
        'responders': ResponderSerializer,
        'attachments': AttachmentSerializer,
        'comments': AttachmentSerializer
    }

    class Meta:
        model = Ticket
        read_only_fields = ('requester', 'responders', 'users')
        fields = (
            'id',
            'responders',
            'requester',
            'users',

            'kind',
            'request_type',
            'status',
            'sensitive',
            'whysensitive',
            'deadline_at',
            'created_at',
            'updated_at',

            'background',
            'first_name',
            'last_name',
            'born_at',
            'connections',
            'sources',
            'business_activities',
            'initial_information',
            'company_name',
            'country'
        )


class ActionRelatedField(relations.ResourceRelatedField):
    """Custom polymorphic serializer for action types."""

    def get_attribute(self, instance):
        not_comment = (
            self.field_name == 'comment' and
            not isinstance(instance.action, Comment))
        not_attachment = (
            self.field_name == 'attachment' and
            not isinstance(instance.action, Attachment))
        not_responder_user = (
            self.field_name == 'responder_user' and
            not isinstance(instance.action, Profile))

        if not_comment or not_attachment or not_responder_user:
            raise fields.SkipField()

        return super(ActionRelatedField, self).get_attribute(instance)


class ActionSerializer(serializers.ModelSerializer):

    included_serializers = {
        'user': ProfileSerializer,
        'responder_user': ProfileSerializer,
        'comment': CommentSerializer,
        'attachment': AttachmentSerializer,
        'ticket': TicketSerializer
    }

    user = relations.ResourceRelatedField(read_only=True, source='actor')
    ticket = relations.ResourceRelatedField(read_only=True, source='target')

    comment = ActionRelatedField(read_only=True, source='action')
    attachment = ActionRelatedField(read_only=True, source='action')
    responder_user = ActionRelatedField(read_only=True, source='action')
    responder_user = ActionRelatedField(read_only=True, source='action')
    created_at = fields.DateTimeField(
        read_only=True, source='timestamp')

    class Meta:
        model = Action
        resource_name = 'Activity'
        fields = (
            'user',
            'verb',
            'ticket',
            'attachment',
            'comment',
            'responder_user',
            'created_at'
        )
