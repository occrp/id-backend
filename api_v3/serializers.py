from rest_framework_json_api import serializers, relations

from .models import Profile, Ticket, Attachment, Comment, Action


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
        read_only_fields = ('requester', 'responders')
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


class AttachmentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Attachment
        read_only_fields = ('user',)
        fields = (
            'id',
            'user',
            'ticket',
            'upload',
            'created_at'
        )


class CommentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Comment
        read_only_fields = ('user',)
        fields = (
            'id',
            'user',
            'ticket',
            'body',
            'created_at'
        )


class ActionSerializer(serializers.ModelSerializer):

    actor = relations.ResourceRelatedField(read_only=True)
    action = relations.ResourceRelatedField(read_only=True)
    target = relations.ResourceRelatedField(read_only=True)

    class Meta:
        model = Action
        fields = ('actor', 'action', 'verb', 'target')
