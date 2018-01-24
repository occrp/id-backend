from rest_framework_json_api import serializers

from api_v3.models import Responder


class ResponderSerializer(serializers.ModelSerializer):

    included_serializers = {
        'user': 'api_v3.serializers.ProfileSerializer',
        'ticket': 'api_v3.serializers.TicketSerializer'
    }

    class Meta:
        model = Responder
        fields = ('ticket', 'user')
        resource_name = 'responders'
