from rest_framework import viewsets

from api_v3.models import Action, Ticket
from api_v3.serializers import ActionSerializer
from .support import JSONApiEndpoint


class ActivitiesEndpoint(JSONApiEndpoint, viewsets.ReadOnlyModelViewSet):
    queryset = Action.objects.all()
    serializer_class = ActionSerializer
    ordering_fields = ('timestamp',)
    ordering = ('-timestamp',)
    filter_fields = {
        'id': ['exact', 'lt', 'gt'],
        'timestamp': ['range'],
        'target_object_id': ['exact'],
        'actor_object_id': ['exact'],
        'verb': ['exact']
    }

    def get_queryset(self):
        queryset = super(ActivitiesEndpoint, self).get_queryset()

        if self.request.user.is_superuser:
            return queryset

        # If this is anonymous, for some reason DRF evaluates the
        # authentication after the queryset
        if not self.request.user.is_active:
            return queryset.none()

        user_ticket_ids = Ticket.filter_by_user(
            self.request.user).values_list('id', flat=True)
        return Action.objects.filter(
            target_object_id__in=map(str, user_ticket_ids))
