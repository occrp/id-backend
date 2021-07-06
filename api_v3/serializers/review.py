from rest_framework_json_api import serializers

from api_v3.models import Review


class ReviewSerializer(serializers.ModelSerializer):

    token = serializers.SerializerMethodField()

    class Meta:
        model = Review

        read_only_fields = (
            'token',
        )

        fields = (
            'id',
            'rating',
            'link',
            'body',
            'created_at',
            'token',
        )

    def get_token(self, obj):
        """Just to make the attribute present in the payload."""
        return None
