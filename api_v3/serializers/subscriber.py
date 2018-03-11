from api_v3.models import Subscriber
from .mixins import ResponderSubscriberSerializer


class SubscriberSerializer(ResponderSubscriberSerializer):

    included_serializers = {
        'user': 'api_v3.serializers.ProfileSerializer',
        'ticket': 'api_v3.serializers.TicketSerializer'
    }

    class Meta:
        model = Subscriber
        fields = ('ticket', 'user')
        resource_name = 'subscribers'
        validators = ResponderSubscriberSerializer.UNIQUENESS_VALIDATORS
