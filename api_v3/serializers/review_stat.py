import hashlib

from rest_framework import fields
from rest_framework_json_api import serializers
from rest_framework_json_api import relations

from api_v3.models import Profile, Ticket


class ReviewStatSerializer(serializers.Serializer):

    class Meta:
        resource_name = 'review-stats'

    id = fields.SerializerMethodField()
    count = serializers.IntegerField()
    ratings = serializers.IntegerField()
    ticket = relations.SerializerMethodResourceRelatedField(
        required=False, model=Ticket
    )
    responder = relations.SerializerMethodResourceRelatedField(
        required=False, model=Profile
    )

    def get_ticket(self, instance):
        return instance.ticket

    def get_responder(self, instance):
        return instance.responder

    def get_id(self, data):
        pk = hashlib.sha256(
            (
                str(data.get('responder_id') or '') +
                str(data.get('ticket_id') or '')
            ).encode('utf-8')
        ).hexdigest()
        # Leave this mocked pk, or DRF will complain
        data.pk = pk
        return pk
