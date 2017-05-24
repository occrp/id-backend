from rest_framework_json_api import serializers

from .models import Profile, Ticket, Notification, Attachment

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
            'responders',
            'requester',

            'kind',
            'request_type',
            'status',
            'sensitive',
            'whysensitive',
            'deadline_at',
            'created_at',
            'updated_at',

            'background',
            'first_name',
            'last_name',
            'born_at',
            'connections',
            'sources',
            'activities',
            'initial_information',
            'company_name',
            'country'
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


class AttachmentSerializer(serializers.ModelSerializer):
    user = ProfileSerializer(required=False)

    class Meta:
        model = Attachment
        fields = (
            'id',
            'user',
            'ticket',
            'upload',
            'created_at'
        )
