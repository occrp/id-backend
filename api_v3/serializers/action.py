from rest_framework import fields
from rest_framework_json_api import serializers, relations

from api_v3.models import Action, Attachment, Comment, Profile
from .attachment import AttachmentSerializer
from .comment import CommentSerializer
from .profile import ProfileSerializer


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
        'user': 'api_v3.serializers.ProfileSerializer',
        'attachment': 'api_v3.serializers.AttachmentSerializer',
        'comment': 'api_v3.serializers.CommentSerializer',
        'responder_user': 'api_v3.serializers.ProfileSerializer',
        'ticket': 'api_v3.serializers.TicketSerializer'
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
        resource_name = 'activities'
        fields = (
            'user',
            'verb',
            'ticket',
            'attachment',
            'comment',
            'responder_user',
            'created_at'
        )
