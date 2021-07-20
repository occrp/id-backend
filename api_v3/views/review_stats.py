from datetime import datetime, timedelta

from django.db.models import Count, F, Sum
from django.db.models.functions import Trunc
from rest_framework import viewsets, response

from api_v3.models import Profile, Review, Ticket
from api_v3.serializers import ReviewStatSerializer
from .support import JSONApiEndpoint


class ReviewStatsEndpoint(JSONApiEndpoint, viewsets.ReadOnlyModelViewSet):

    class Pagination(JSONApiEndpoint.pagination_class):
        page_size = None

    class ReviewStat(dict):
        __getattr__ = dict.__getitem__
        __setattr__ = dict.__setitem__

    queryset = Review.objects.all()
    serializer_class = ReviewStatSerializer
    pagination_class = Pagination
    filter_fields = {
        'created_at': ['gte', 'lte'],
        'ticket': ['exact', 'isnull'],
        'ticket__responders__user': ['exact', 'isnull']
    }

    def extract_filter_params(self, request):
        """Set default filter values."""
        params = super(
            ReviewStatsEndpoint, self).extract_filter_params(request)

        if not params.get('created_at__gte'):
            three_months_ago = (
                datetime.utcnow().replace(day=1) - timedelta(days=28 * 3))
            params['created_at__gte'] = three_months_ago.replace(
                day=1, hour=0, minute=0, second=0, microsecond=0).isoformat()

        return params

    def list(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            return response.Response(self.serializer_class([], many=True).data)

        queryset = self.filter_queryset(self.get_queryset())
        group_by = None

        annotations = dict(
            t_id=F('ticket_id'),
            responder_id=F('ticket__responders__user_id'),
            count=Count('id'),
            ratings=Sum('rating')
        )

        if request.GET.get('by') == 'responder':
            group_by = ('responder_id',)
            del annotations['t_id']
        else:
            group_by = ('t_id',)
            del annotations['responder_id']

        aggregated = queryset.annotate(**annotations).values(
            *annotations.keys())
        aggregated.query.group_by = group_by

        stats = [
            self.ReviewStat(
                stat,
                ticket_id=stat.get('t_id'),
                ticket=Ticket.objects.filter(id=stat.get('t_id')).first(),
                responder_id=stat.get('responder_id'),
                responder=Profile.objects.filter(
                    id=stat.get('responder_id')
                ).first(),
                pk=None
            ) for stat in list(aggregated)
        ]
        serializer = self.serializer_class(stats, many=True)

        return response.Response(serializer.data)
