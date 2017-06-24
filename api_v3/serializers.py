from rest_framework_json_api import serializers, relations
from rest_framework import fields

from .models import Profile, Ticket, Action, Attachment, Comment, Responder


class ProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = Profile
        fields = (
            'id',
            'email',
            'first_name',
            'last_name',
            'is_staff',
            'is_superuser',
            'locale'
        )


class ResponderSerializer(serializers.ModelSerializer):

    class Meta:
        model = Responder
        fields = ('ticket', 'user')
        resource_name = 'Responder'


class AttachmentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Attachment
        read_only_fields = ('user',)
        fields = (
            'id',
            'user',
            'ticket',
            'upload',
            'created_at'
        )


class CommentSerializer(serializers.ModelSerializer):

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
        'requester': ProfileSerializer,
        'responder': ResponderSerializer,
        'attachments': AttachmentSerializer
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

    user = relations.ResourceRelatedField(read_only=True, source='actor')
    ticket = relations.ResourceRelatedField(read_only=True, source='target')

    comment = ActionRelatedField(read_only=True, source='action')
    attachment = ActionRelatedField(read_only=True, source='action')
    responder_user = ActionRelatedField(read_only=True, source='action')

    class Meta:
        model = Action
        resource_name = 'Activity'
        fields = (
            'user',
            'verb',
            'ticket',
            'attachment',
            'comment',
            'responder_user'
        )
