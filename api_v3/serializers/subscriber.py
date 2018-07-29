from rest_framework_json_api import serializers

from api_v3.models import Subscriber
from .mixins import ResponderSubscriberSerializer


class SubscriberSerializer(ResponderSubscriberSerializer):

    included_serializers = {
        'user': 'api_v3.serializers.ProfileSerializer',
        'ticket': 'api_v3.serializers.TicketSerializer'
    }

    class Meta:
        model = Subscriber
        fields = ('ticket', 'user', 'email',)
        validators = (
            ResponderSubscriberSerializer.UNIQUENESS_VALIDATORS +
            ResponderSubscriberSerializer.EMAIL_UNIQUENESS_VALIDATORS
        )

    email = serializers.CharField(required=False, default=None)
