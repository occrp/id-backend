import os.path

import magic
from rest_framework_json_api import serializers, relations
from rest_framework import fields

from .models import Profile, Ticket, Action, Attachment, Comment, Responder


class ProfileSerializer(serializers.ModelSerializer):

    tickets_count = fields.SerializerMethodField()

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
            'bio',
            'locale',
            'tickets_count'
        )

    def get_tickets_count(self, obj):
        return Ticket.filter_by_user(obj).count()


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
        'comments': CommentSerializer
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


class ActionRelatedField(relations.PolymorphicResourceRelatedField):
    """Custom polymorphic serializer for action types."""

    def get_attribute(self, instance):
        obj = instance.action
        self.source = 'action'

        is_comment = self.field_name == 'comment' and isinstance(obj, Comment)
        is_attachment = (
            self.field_name == 'attachment' and isinstance(obj, Attachment))
        is_responder_user = (
            self.field_name == 'responder_user' and isinstance(obj, Profile))

        if is_comment or is_attachment or is_responder_user:
            try:
                return super(ActionRelatedField, self).get_attribute(instance)
            except AttributeError:
                return obj

        raise fields.SkipField()


class ActionSerializer(serializers.ModelSerializer):

    included_serializers = {
        'user': ProfileSerializer,
        'attachment': AttachmentSerializer,
        'comment': CommentSerializer,
        'responder_user': ProfileSerializer,
        'ticket': TicketSerializer
    }

    user = relations.ResourceRelatedField(read_only=True, source='actor')
    ticket = relations.ResourceRelatedField(read_only=True, source='target')

    comment = ActionRelatedField(CommentSerializer, read_only=True)
    attachment = ActionRelatedField(AttachmentSerializer, read_only=True)
    responder_user = ActionRelatedField(ProfileSerializer, read_only=True)
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
