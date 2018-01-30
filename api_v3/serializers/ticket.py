from rest_framework_json_api import serializers

from api_v3.models import Profile, Ticket


class TicketSerializer(serializers.ModelSerializer):

    included_serializers = {
        'users': 'api_v3.serializers.ProfileSerializer',
        'requester': 'api_v3.serializers.ProfileSerializer',
        'responders': 'api_v3.serializers.ResponderSerializer',
        'attachments': 'api_v3.serializers.AttachmentSerializer'
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
        except Exception:
            user = None

        if user and user.is_superuser:
            tickets = Ticket.objects.all()
        else:
            tickets = Ticket.filter_by_user(user)

        for status in Ticket.STATUSES:
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
