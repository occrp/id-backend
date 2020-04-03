from rest_framework import fields
from rest_framework_json_api import serializers, relations

from api_v3.models import Action, Attachment, Comment, Expense, Profile
from .comment import CommentSerializer
from .profile import ProfileSerializer


class ActionRelatedField(relations.PolymorphicResourceRelatedField):
    """Custom polymorphic serializer for action types.

    Otherwise it will generate a relationship for every possible type.
    """

    def get_attribute(self, instance):
        obj = super(ActionRelatedField, self).get_attribute(instance)

        is_comment = self.field_name == 'comment' and isinstance(obj, Comment)
        is_expense = self.field_name == 'expense' and isinstance(obj, Expense)
        is_attachment = (
            self.field_name == 'attachment' and isinstance(obj, Attachment))
        is_responder_user = (
            self.field_name == 'responder_user' and isinstance(obj, Profile))

        if is_comment or is_expense or is_attachment or is_responder_user:
            return obj

        raise fields.SkipField()


class ActionPolymorphicSerializer(serializers.PolymorphicModelSerializer):
    polymorphic_serializers = [
        ProfileSerializer,
        CommentSerializer
    ]


class ActionSerializer(serializers.ModelSerializer):

    included_serializers = {
        'user': 'api_v3.serializers.ProfileSerializer',
        'comment': 'api_v3.serializers.CommentSerializer',
        'responder_user': 'api_v3.serializers.ProfileSerializer',
        'ticket': 'api_v3.serializers.TicketSerializer'
    }

    user = relations.ResourceRelatedField(read_only=True, source='actor')
    ticket = relations.ResourceRelatedField(read_only=True, source='target')

    comment = ActionRelatedField(
        ActionPolymorphicSerializer, source='action', read_only=True)
    expense = ActionRelatedField(
        ActionPolymorphicSerializer, source='action', read_only=True)
    attachment = ActionRelatedField(
        ActionPolymorphicSerializer, source='action', read_only=True)
    responder_user = ActionRelatedField(
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
            'expense',
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
