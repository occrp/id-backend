from rest_framework_json_api import serializers

from api_v3.models import Comment


class CommentSerializer(serializers.ModelSerializer):

    included_serializers = {
        'user': 'api_v3.serializers.ProfileSerializer',
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
