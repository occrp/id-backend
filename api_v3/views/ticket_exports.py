from csv import DictWriter
from datetime import datetime

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
    permission_classes = (permissions.IsAdminUser, )

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        ticket_url = 'https://{}/tickets/view/'.format(self.request.get_host())
        qdata = queryset.values(
            Link=Concat(models.Value(ticket_url), models.F('id')),
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

        writer = DictWriter(DummyBuffer(), fieldnames=qdata.first().keys())
        response = StreamingHttpResponse(
            (writer.writerow(row) for row in qdata), content_type='text/csv')

        response['Content-Disposition'] = (
            'attachment; filename="tickets-{}.csv"'.format(
                datetime.utcnow().strftime('%x')))

        return response
