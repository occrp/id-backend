from rest_framework import fields
from rest_framework_json_api import serializers, relations

from api_v3.models import Action
from .attachment import AttachmentSerializer
from .comment import CommentSerializer
from .profile import ProfileSerializer


class ActionPolymorphicSerializer(serializers.PolymorphicModelSerializer):
    polymorphic_serializers = [
        ProfileSerializer,
        AttachmentSerializer,
        CommentSerializer
    ]


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

    comment = relations.PolymorphicResourceRelatedField(
        ActionPolymorphicSerializer, source='action', read_only=True)
    attachment = relations.PolymorphicResourceRelatedField(
        ActionPolymorphicSerializer, source='action', read_only=True)
    responder_user = relations.PolymorphicResourceRelatedField(
        ActionPolymorphicSerializer, source='action', read_only=True)
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

    def get_root_meta(self, obj, many):
        """Adds extra root meta details."""
        view = self.context.get('view') if self.context else None
        queryset = view.filter_queryset(view.get_queryset()) if view else None

        if not many or not queryset or not queryset.exists():
            return {}

        return {
            'last_id': str(queryset.last().id),
            'first_id': str(queryset.first().id)
        }
