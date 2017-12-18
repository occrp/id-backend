import os.path
import hashlib
from datetime import datetime

import magic
from django.urls import reverse
from rest_framework_json_api import serializers, relations
from rest_framework import fields

from .models import(
    Profile, Ticket, Action, Attachment, Comment, Responder, TICKET_STATUS)


class ProfileSerializer(serializers.ModelSerializer):

    tickets_count = fields.SerializerMethodField()

    class Meta:
        model = Profile
        read_only_fields = (
            'id',
            'email',
            'first_name',
            'last_name',
            'is_staff',
            'is_superuser',
            'locale'
        )
        fields = (
            'id',
            'email',
            'first_name',
            'last_name',
            'is_staff',
            'is_superuser',
            'bio',
            'locale',
            'tickets_count'
        )

    def get_tickets_count(self, obj):
        return Ticket.filter_by_user(obj).count()

    def to_representation(self, obj):
        request = self.context.get('request', None)

        data = super(ProfileSerializer, self).to_representation(obj)

        if request and request.user and request.user.is_superuser:
            return data

        # For regular users, make sure others email is not displayed
        if request and request.user != obj:
            data.pop('email')

        return data


class ResponderSerializer(serializers.ModelSerializer):

    included_serializers = {
        'user': ProfileSerializer,
        'ticket': 'api_v3.serializers.TicketSerializer'
    }

    class Meta:
        model = Responder
        fields = ('ticket', 'user')
        resource_name = 'responders'


class AttachmentFileField(serializers.FileField):

    def to_representation(self, obj):
        if obj.instance.upload and self.context.get('request', None):
            return self.context['request'].build_absolute_uri(
                reverse('download-detail', args=[obj.instance.id])
            )


class AttachmentSerializer(serializers.ModelSerializer):

    included_serializers = {
        'user': ProfileSerializer,
        'ticket': 'api_v3.serializers.TicketSerializer'
    }

    file_name = serializers.SerializerMethodField()
    file_size = serializers.SerializerMethodField()
    mime_type = serializers.SerializerMethodField()
    upload = AttachmentFileField()

    class Meta:
        model = Attachment
        read_only_fields = ('user',)
        fields = (
            'id',
            'user',
            'ticket',
            'upload',
            'file_name',
            'file_size',
            'mime_type',
            'created_at'
        )

    def get_file_name(self, obj):
        if obj.upload:
            return os.path.basename(obj.upload.name)

    def get_file_size(self, obj):
        if obj.upload and os.path.exists(obj.upload.path):
            return obj.upload.size
        return 0

    def get_mime_type(self, obj):
        if obj.upload and os.path.exists(obj.upload.path):
            return magic.from_file(obj.upload.path, mime=True)


class CommentSerializer(serializers.ModelSerializer):

    included_serializers = {
        'user': ProfileSerializer,
        'ticket': 'api_v3.serializers.TicketSerializer'
    }

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


class TicketSerializer(serializers.ModelSerializer):

    included_serializers = {
        'users': ProfileSerializer,
        'requester': ProfileSerializer,
        'responders': ResponderSerializer,
        'attachments': AttachmentSerializer
    }

    reopen_reason = serializers.SerializerMethodField()
    pending_reason = serializers.SerializerMethodField()

    class Meta:
        model = Ticket
        read_only_fields = (
            'requester',
            'responders',
            'users',
            'attachments',
            'reopen_reason'
        )
        fields = (
            'id',
            'responders',
            'requester',
            'users',

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
            'business_activities',
            'initial_information',
            'company_name',
            'country',
            'attachments',

            'reopen_reason',
            'pending_reason'
        )

    def get_reopen_reason(self, obj):
        """Just to make the attribute present."""
        return None

    def get_pending_reason(self, obj):
        """Just to make the attribute present."""
        return None

    def get_request_filters(self):
        """Returns the request filters based on the ticket profiles."""
        view = self.context.get('view') if self.context else None
        request = self.context.get('request') if self.context else None

        filters = {}
        filter_params = {}
        filter_name_map = {
            'requester': 'requester',
            'responders__user': 'responder'
        }

        if view and request:
            filter_params = view.extract_filter_params(request)

        for filter_param, meta_name in filter_name_map.items():
            profile_id = filter_params.get(filter_param) or ''
            profile_id = int(profile_id) if profile_id.isdigit() else None

            profiles = Profile.objects.filter(id=profile_id).values(
                'first_name', 'last_name', 'email')

            if profiles:
                filters[meta_name] = profiles[0]

        return filters

    def get_ticket_totals(self):
        """Returns the ticket totals based on the status."""
        total = {}

        try:
            user = self.context.get('request').user
        except:
            user = None

        if user and user.is_superuser:
            tickets = Ticket.objects.all()
        else:
            tickets = Ticket.filter_by_user(user)

        for status in TICKET_STATUS:
            status = status[0]
            total[status] = tickets.filter(status=status).count()

        total['all'] = tickets.count()

        return total

    def get_root_meta(self, obj, many):
        """Adds extra root meta details."""
        if many:
            return {
                'total': self.get_ticket_totals(),
                'filters': self.get_request_filters()
            }
        else:
            return {'total': self.get_ticket_totals()}


class ActionRelatedField(relations.PolymorphicResourceRelatedField):
    """Custom polymorphic serializer for action types."""

    def get_attribute(self, instance):
        obj = instance.action
        self.source = 'action'

        is_comment = self.field_name == 'comment' and isinstance(obj, Comment)
        is_attachment = (
            self.field_name == 'attachment' and isinstance(obj, Attachment))
        is_responder_user = (
            self.field_name == 'responder_user' and isinstance(obj, Profile))

        if is_comment or is_attachment or is_responder_user:
            try:
                return super(ActionRelatedField, self).get_attribute(instance)
            except AttributeError:
                return obj

        raise fields.SkipField()


class ActionSerializer(serializers.ModelSerializer):

    included_serializers = {
        'user': ProfileSerializer,
        'attachment': AttachmentSerializer,
        'comment': CommentSerializer,
        'responder_user': ProfileSerializer,
        'ticket': TicketSerializer
    }

    user = relations.ResourceRelatedField(read_only=True, source='actor')
    ticket = relations.ResourceRelatedField(read_only=True, source='target')

    comment = ActionRelatedField(CommentSerializer, read_only=True)
    attachment = ActionRelatedField(AttachmentSerializer, read_only=True)
    responder_user = ActionRelatedField(ProfileSerializer, read_only=True)
    created_at = fields.DateTimeField(
        read_only=True, source='timestamp')

    class Meta:
        model = Action
        resource_name = 'activities'
        fields = (
            'user',
            'verb',
            'ticket',
            'attachment',
            'comment',
            'responder_user',
            'created_at'
        )


class TicketStatSerializer(serializers.Serializer):

    included_serializers = {
        'profile': ProfileSerializer,
    }

    class Meta:
        resource_name = 'ticket-stats'

    id = fields.SerializerMethodField()
    date = serializers.DateTimeField()
    count = serializers.IntegerField()
    status = serializers.CharField(source='ticket_status')
    avg_time = fields.SerializerMethodField()
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

    def get_avg_time(self, data):
        """Returns the avg. time in days."""
        return data.get('avg_time').days

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
