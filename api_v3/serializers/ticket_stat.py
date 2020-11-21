import hashlib

from rest_framework import fields
from rest_framework_json_api import serializers
from rest_framework_json_api import relations

from api_v3.models import Profile


class TicketStatSerializer(serializers.Serializer):

    included_serializers = {
        'responder': 'api_v3.serializers.ProfileSerializer',
    }

    class Meta:
        resource_name = 'ticket-stats'

    id = fields.SerializerMethodField()
    date = serializers.DateTimeField(required=False)
    count = serializers.IntegerField()
    status = serializers.CharField(source='ticket_status')
    country = serializers.CharField(source='ticket_country', required=False)
    avg_time = fields.IntegerField()
    past_deadline = fields.IntegerField()
    responder = relations.SerializerMethodResourceRelatedField(
        required=False, model=Profile
    )

    def get_responder(self, instance):
        return instance.responder

    def get_id(self, data):
        pk = hashlib.sha256(
            (
                data.get('ticket_status') +
                str(data.get('date') or '') +
                str(data.get('responder_id') or '') +
                str(data.get('country') or '')
            ).encode('utf-8')
        ).hexdigest()
        # Leave this mocked pk, or DRF will complain
        data.pk = pk
        return pk
