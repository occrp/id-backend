from api_v3.models import Responder
from .mixins import ResponderSubscriberSerializer


class ResponderSerializer(ResponderSubscriberSerializer):

    included_serializers = {
        'user': 'api_v3.serializers.ProfileSerializer',
        'ticket': 'api_v3.serializers.TicketSerializer'
    }

    class Meta:
        model = Responder
        fields = ('ticket', 'user')
        resource_name = 'responders'
        validators = ResponderSubscriberSerializer.UNIQUENESS_VALIDATORS
