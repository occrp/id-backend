from csv import DictWriter
from datetime import datetime

from django.db import models
from django.db.models.functions import Concat
from django.http import StreamingHttpResponse
from rest_framework import permissions

from .expenses import ExpensesEndpoint
from .ticket_exports import TicketExportsEndpoint, DummyBuffer


class ExpenseExportsEndpoint(ExpensesEndpoint):
    permission_classes = (permissions.IsAdminUser, )

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        ticket_url = \
            TicketExportsEndpoint.TICKET_URI.format(self.request.get_host())

        qdata = queryset.values(
            Link=Concat(models.Value(ticket_url), models.F('ticket_id')),
            Date=models.F('created_at'),
            Status=models.F('ticket__status'),
            Amount=models.F('amount'),
            Currency=models.F('amount_currency'),
            Rating=models.F('rating'),
            Scope=models.F('scope'),
            RequesterCountry=models.F('ticket__requester__country'),
            OriginalCountry=models.F('ticket__country'),
            ExtraCountries=models.Func(
                models.F('ticket__countries'),
                models.Value(','),
                function='ARRAY_TO_STRING'
            )
        )

        writer = DictWriter(DummyBuffer(), fieldnames=qdata.first().keys())
        response = StreamingHttpResponse(
            (writer.writerow(row) for row in qdata), content_type='text/csv')

        response['Content-Disposition'] = (
            'attachment; filename="expenses-{}.csv"'.format(
                datetime.utcnow().strftime('%x')))

        return response
