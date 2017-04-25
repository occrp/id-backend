from rest_framework_json_api import serializers

from .models import Profile, Ticket

class ProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = Profile
        fields = (
            'id',
            'email',
            'first_name',
            'last_name',
            'is_staff',
            'is_superuser',
            'locale'
        )


class TicketSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ticket
        fields = (
            'id',
            'ticket_type',
            'created',
            'status',
            'status_updated',
            'sensitive',
            'whysensitive',
            'deadline',
        )
