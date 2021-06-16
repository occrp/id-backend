from datetime import datetime, timedelta

from django.db.models import (
    Avg, Count, Case, F, Func, DurationField, ExpressionWrapper,
    IntegerField, Sum, When)
from django.db.models.functions import Trunc, Extract
from rest_framework import viewsets, response

from api_v3.models import Profile, Ticket
from api_v3.serializers import TicketStatSerializer
from .support import JSONApiEndpoint


class TicketStatsEndpoint(JSONApiEndpoint, viewsets.ReadOnlyModelViewSet):

    class Pagination(JSONApiEndpoint.pagination_class):
        page_size = None

    class TicketStat(dict):
        __getattr__ = dict.__getitem__
        __setattr__ = dict.__setitem__

    queryset = Ticket.objects.all()
    serializer_class = TicketStatSerializer
    pagination_class = Pagination
    filter_fields = {
        'created_at': ['gte', 'lte'],
        'country': ['exact'],
        'status': ['in'],
        'kind': ['exact'],
        'responders__user': ['exact', 'isnull']
    }

    def extract_filter_params(self, request):
        """Set default filter values."""
        params = super(
            TicketStatsEndpoint, self).extract_filter_params(request)

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
            date=Trunc('created_at', 'month'),
            responder_id=F('responders__user_id'),
            ticket_country=Func(F('countries'), function='unnest'),
            count=Count('id'),
            ticket_status=F('status'),
            avg_time=Avg(
                Extract(
                    ExpressionWrapper(
                        (
                            (F('updated_at') - F('created_at')) / (60 * 60)
                        ),
                        output_field=DurationField()
                    ),
                    lookup_name='epoch'
                )
            ),
            past_deadline=Sum(
                Case(
                    When(updated_at__gt=F('deadline_at'), then=1),
                    default=0,
                    output_field=IntegerField()
                )
            )
        )

        if request.GET.get('by') == 'country':
            group_by = ('ticket_country', 'status')
            del annotations['date']
            del annotations['responder_id']
        elif request.GET.get('by') == 'responder':
            group_by = ('responder_id', 'status')
            del annotations['date']
            del annotations['ticket_country']
        else:
            group_by = ('date', 'status')
            del annotations['responder_id']
            del annotations['ticket_country']

        aggregated = queryset.annotate(**annotations).values(
            *annotations.keys())
        aggregated.query.group_by = group_by

        stats = [
            self.TicketStat(
                stat,
                responder_id=stat.get('responder_id'),
                responder=Profile.objects.filter(
                    id=stat.get('responder_id')
                ).first(),
                pk=None
            ) for stat in list(aggregated)
        ]
        serializer = self.serializer_class(stats, many=True)

        return response.Response(serializer.data)
