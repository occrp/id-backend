from rest_framework_json_api import serializers

from .models import Profile, Ticket, Notification

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


class NotificationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Notification
        fields = (
            'id',
            'timestamp',
            'is_seen',
            'text',
            'url_base',
            'url_params',
            'url',
            'project',
            'module',
            'model',
            'instance',
            'action',
            'user'
        )
