import os.path

from django.http import FileResponse
from rest_framework import viewsets, exceptions, permissions

from api_v3.models import Attachment, Ticket
from .support import JSONApiEndpoint


class DownloadEndpoint(JSONApiEndpoint, viewsets.ViewSet):

    permission_classes = (permissions.IsAuthenticated,)

    def retrieve(self, request, pk=None):
        user_ticket_ids = Ticket.filter_by_user(
            self.request.user).values_list('id', flat=True)

        if self.request.user.is_superuser:
            attachment = Attachment.objects.get(id=pk)
        else:
            attachment = Attachment.objects.filter(
                id=pk, ticket__in=user_ticket_ids).first()

        if not attachment or not attachment.upload:
            raise exceptions.NotFound()

        return FileResponse(
            attachment.upload.file,
            content_type='application/octet-stream',
            as_attachment=True
        )

        return resp
