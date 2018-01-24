from datetime import datetime
import hashlib

from rest_framework import fields
from rest_framework_json_api import serializers

from .profile import ProfileSerializer


class TicketStatSerializer(serializers.Serializer):

    included_serializers = {
        'profile': 'api_v3.serializers.ProfileSerializer',
    }

    class Meta:
        resource_name = 'ticket-stats'

    id = fields.SerializerMethodField()
    date = serializers.DateTimeField()
    count = serializers.IntegerField()
    status = serializers.CharField(source='ticket_status')
    avg_time = fields.IntegerField()
    past_deadline = fields.IntegerField()
    profile = ProfileSerializer()

    def get_id(self, data):
        pk = hashlib.sha256(
            str(self.context.get('params')) +
            str(data.get('date')) +
            data.get('ticket_status') +
            str(data.profile.id if data.get('profile') else '')
        ).hexdigest()
        # Leave this mocked pk, or DRF will complain
        data.pk = pk
        return pk

    def get_root_meta(self, data, many):
        """Adds extra root meta details."""
        params = self.context.get('params')

        # Do not include meta on when no data.
        if not self.instance:
            return {}

        return {
            'total': self.context.get('totals'),
            'countries': self.context.get('countries'),
            'staff_profile_ids': self.context.get('responder_ids'),
            'start_date': params.get('created_at__gte'),
            'end_date': (
                params.get('created_at__lte') or
                datetime.utcnow().isoformat()
            )
        }
