from csv import DictWriter
from datetime import datetime
from itertools import chain

from django.db import models
from django.db.models.functions import Concat
from django.http import StreamingHttpResponse
from rest_framework import permissions

from .reviews import ReviewsEndpoint
from .ticket_exports import TicketExportsEndpoint, DummyBuffer


class ReviewExportsEndpoint(ReviewsEndpoint):
    permission_classes = (permissions.IsAdminUser, )

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        ticket_url = \
            TicketExportsEndpoint.TICKET_URI.format(self.request.get_host())

        cols = dict(
            Ticket=Concat(
                models.Value(ticket_url),
                models.F('ticket_id'),
                output_field=models.CharField()
            ),
            Date=models.F('created_at'),
            Rating=models.F('rating'),
            Link=models.F('link'),
            Comment=models.F('body')
        )

        writer = DictWriter(DummyBuffer(), fieldnames=cols.keys())
        header_with_rows = chain(
            [dict(zip(cols.keys(), cols.keys()))],
            queryset.values(**cols)
        )

        response = StreamingHttpResponse(
            streaming_content=(
                writer.writerow(row) for row in header_with_rows
            ),
            content_type='text/csv'
        )

        response['Content-Disposition'] = (
            'attachment; filename="reviews-{}.csv"'.format(
                datetime.utcnow().strftime('%x')))

        return response
