from datetime import datetime, timedelta

from django.db.models import Avg, Count, Case, F, IntegerField, Sum, When
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
                datetime.utcnow().replace(day=1) - timedelta(days=28*3))
            params['created_at__gte'] = three_months_ago.replace(
                day=1, hour=0, minute=0, second=0, microsecond=0).isoformat()

        return params

    def list(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            return response.Response(self.serializer_class([], many=True).data)

        profile = None
        countries = []
        responder_ids = []
        params = self.extract_filter_params(self.request)
        queryset = self.filter_queryset(self.get_queryset())

        if not params.get('responders__user') and not params.get('country'):
            responder_ids = queryset.filter(
                responders__user__isnull=False
            ).values_list('responders__user', flat=1).distinct()
            countries = queryset.filter(
                country__isnull=False
            ).values_list('country', flat=1).order_by('country').distinct()
        elif params.get('responders__user'):
            profile = Profile.objects.get(id=params.get('responders__user'))

        totals = queryset.aggregate(
            all=Count('id'),
            new=Sum(
                Case(
                    When(status='new', then=1), default=0,
                    output_field=IntegerField()
                )
            ),
            in_progress=Sum(
                Case(
                    When(status='in-progress', then=1),
                    default=0,
                    output_field=IntegerField()
                )
            ),
            pending=Sum(
                Case(
                    When(status='pending', then=1),
                    default=0,
                    output_field=IntegerField()
                )
            ),
            closed=Sum(
                Case(
                    When(status='closed', then=1),
                    default=0,
                    output_field=IntegerField()
                )
            ),
            cancelled=Sum(
                Case(
                    When(status='cancelled', then=1),
                    default=0,
                    output_field=IntegerField()
                )
            ),
            open=Sum(
                Case(
                    When(status__in=['new', 'in-progress', 'pending'], then=1),
                    default=0,
                    output_field=IntegerField()
                )
            ),
            avg_time_open=Avg(
                Case(
                    When(
                        status__in=['new', 'in-progress', 'pending'],
                        then=Extract(
                            (F('updated_at') - F('created_at')) / (60 * 60),
                            lookup_name='epoch'
                        )
                    ),
                    default=0,
                    output_field=IntegerField()
                )
            ),
            resolved=Sum(
                Case(
                    When(status__in=['closed', 'cancelled'], then=1),
                    default=0,
                    output_field=IntegerField()
                )
            ),
            avg_time_resolved=Avg(
                Case(
                    When(
                        status__in=['closed', 'cancelled'],
                        then=Extract(
                            (F('updated_at') - F('created_at')) / (60 * 60),
                            lookup_name='epoch'
                        )
                    ),
                    default=0,
                    output_field=IntegerField()
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

        aggregated = queryset.annotate(
            date=Trunc('created_at', 'month'),
            count=Count('id'),
            ticket_status=F('status'),
            avg_time=Avg(
                Extract(
                    (F('updated_at') - F('created_at')) / (60 * 60),
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
        ).values('date', 'count', 'ticket_status', 'avg_time', 'past_deadline')

        # Do not group by automatically.
        aggregated.query.group_by = aggregated.query.group_by[-2:]

        stats = map(
            lambda stat: self.TicketStat(stat, profile=profile, pk=None),
            list(aggregated)
        )

        serializer = self.serializer_class(stats, many=True, context={
            'params': params,
            'totals': totals,
            'countries': countries,
            'responder_ids': responder_ids,
        })

        return response.Response(serializer.data)
