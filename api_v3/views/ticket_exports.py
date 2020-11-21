from csv import DictWriter
from datetime import datetime
from itertools import chain

from django.db import models
from django.db.models.functions import Concat
from django.http import StreamingHttpResponse
from rest_framework import permissions

from .tickets import TicketsEndpoint


class DummyBuffer:
    """Dummy buffer to help stream the response."""
    def write(self, value):
        return value


class TicketExportsEndpoint(TicketsEndpoint):
    TICKET_URI = 'https://{}/tickets/view/'

    permission_classes = (permissions.IsAdminUser, )

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        ticket_url = self.TICKET_URI.format(self.request.get_host())

        cols = dict(
            Link=Concat(models.Value(ticket_url), models.F('id')),
            Email=models.F('requester__email'),
            Date=models.F('created_at'),
            Deadline=models.F('deadline_at'),
            Status=models.F('status'),
            Kind=models.F('kind'),
            RequestType=models.F('request_type'),
            Priority=models.F('priority'),
            RequesterCountry=models.F('requester__country'),
            OriginalCountry=models.F('country'),
            ExtraCountries=models.Func(
                models.F('countries'),
                models.Value(','),
                function='ARRAY_TO_STRING'
            ),
            MemberCenter=models.F('member_center'),
            Tags=models.Func(
                models.F('tags'),
                models.Value(','),
                function='ARRAY_TO_STRING'
            )
        )

        writer = DictWriter(DummyBuffer(), fieldnames=cols.keys())
        header_with_rows = chain(
            [dict(zip(cols.keys(), cols.keys()))],
            queryset.values(**cols)
        )

        response = StreamingHttpResponse(
            streaming_content=(writer.writerow(row) for row in header_with_rows),
            content_type='text/csv'
        )

        response['Content-Disposition'] = (
            'attachment; filename="tickets-{}.csv"'.format(
                datetime.utcnow().strftime('%x')))

        return response
