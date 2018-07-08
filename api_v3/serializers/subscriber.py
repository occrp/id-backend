from rest_framework_json_api import serializers

from api_v3.models import Subscriber
from .mixins import ResponderSubscriberSerializer


class SubscriberSerializer(ResponderSubscriberSerializer):

    included_serializers = {
        'user': 'api_v3.serializers.ProfileSerializer',
        'ticket': 'api_v3.serializers.TicketSerializer'
    }

    user_email = serializers.SerializerMethodField()

    class Meta:
        model = Subscriber
        fields = ('ticket', 'user', 'user_email',)
        validators = ResponderSubscriberSerializer.UNIQUENESS_VALIDATORS

    def get_user_email(self, obj):
        """Just to make the attribute present."""
        return None
