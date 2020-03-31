from datetime import datetime

from rest_framework_json_api import serializers
from rest_framework_json_api.utils import format_field_names

from api_v3.models import Profile, Ticket, countries
from .profile import ProfileSerializer


class ListChoiceField(serializers.MultipleChoiceField):
    """Patched field to always return a list not a set."""
    def to_internal_value(self, data):
        return list(super(ListChoiceField, self).to_internal_value(data))

    def to_representation(self, data):
        return list(super(ListChoiceField, self).to_representation(data))


class TicketSerializer(serializers.ModelSerializer):

    included_serializers = {
        'users': 'api_v3.serializers.ProfileSerializer',
        'responder_users': 'api_v3.serializers.ProfileSerializer',
        'subscriber_users': 'api_v3.serializers.ProfileSerializer',
        'requester': 'api_v3.serializers.ProfileSerializer',
        'responders': 'api_v3.serializers.ResponderSerializer',
        'subscribers': 'api_v3.serializers.SubscriberSerializer'
    }

    reopen_reason = serializers.SerializerMethodField()
    pending_reason = serializers.SerializerMethodField()
    users = ProfileSerializer(many=True, read_only=True)
    countries = ListChoiceField(
        countries.COUNTRIES, allow_blank=False, required=False)
    tags = serializers.ListField(
        child=serializers.CharField(), allow_empty=True, required=False)

    class Meta:
        model = Ticket
        read_only_fields = (
            'requester',
            'responders',
            'subscribers',
            'users',
            'responder_users',
            'subscriber_users',
            'reopen_reason'
        )
        fields = (
            'id',
            'responders',
            'subscribers',
            'requester',
            'users',
            'responder_users',
            'subscriber_users',

            'kind',
            'request_type',
            'status',
            'sensitive',
            'whysensitive',
            'deadline_at',
            'created_at',
            'updated_at',
            'member_center',
            'identifier',
            'countries',
            'tags',

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

            'reopen_reason',
            'pending_reason'
        )

    def validate_deadline_at(self, value):
        """Deadline validation."""
        error = serializers.ValidationError([{
            'data/attributes/deadline_at': 'The date can not be in the past.'
        }])

        if not value:
            return value

        if not self.instance and value < datetime.utcnow():
            raise error
        elif not self.instance:
            return value

        status = self.initial_data.get('status')
        status_changed = self.instance.status != status
        deadline_changed = self.instance.deadline_at != value
        deadline_passed = deadline_changed and value < datetime.utcnow()

        if not status_changed and deadline_passed:
            raise error

        return value

    def get_reopen_reason(self, obj):
        """Just to make the attribute present."""
        return None

    def get_pending_reason(self, obj):
        """Just to make the attribute present."""
        return None

    def get_request_filters(self):
        """Returns the request filters based on the ticket profiles."""
        filters = {}

        try:
            user = self.context.get('request').user
        except Exception:
            user = None

        if not (user and user.is_superuser):
            return filters

        view = self.context.get('view') if self.context else None
        request = self.context.get('request') if self.context else None

        filter_params = {}
        filter_name_map = {
            'requester': 'requester',
            'responders__user': 'responder'
        }

        if view and request:
            filter_params = view.extract_filter_params(request)

        for filter_param, meta_name in list(filter_name_map.items()):
            profile_id = filter_params.get(filter_param) or ''
            profile_id = int(profile_id) if profile_id.isdigit() else None

            profiles = Profile.objects.filter(id=profile_id).values(
                'first_name', 'last_name', 'email')

            if profiles:
                filters[meta_name] = format_field_names(profiles[0])

        return filters

    def get_ticket_totals(self):
        """Returns the ticket totals based on the status."""
        total = {}
        view = self.context.get('view') if self.context else None

        if not view:
            return total

        queryset = view.filter_queryset(view.get_queryset())

        # Reset status filters to gather proper counts.
        for clause in queryset.query.where.children:
            try:
                if clause.lhs.field.name == 'status':
                    queryset.query.where.children.remove(clause)
            except Exception:
                pass

        for status in Ticket.STATUSES:
            status = status[0]
            total[status] = queryset.filter(status=status).count()

        total['all'] = queryset.count()

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
