from rest_framework_json_api import serializers

from api_v3.models import Subscriber


class SubscriberSerializer(serializers.ModelSerializer):

    included_serializers = {
        'user': 'api_v3.serializers.ProfileSerializer',
        'ticket': 'api_v3.serializers.TicketSerializer'
    }

    class Meta:
        model = Subscriber
        fields = ('ticket', 'user')
        resource_name = 'subscribers'
