import os.path

from django.http import FileResponse
from rest_framework import viewsets, exceptions, permissions

from api_v3.models import Attachment, Ticket


class DownloadEndpoint(viewsets.ViewSet):

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

        resp = FileResponse(
            attachment.upload.file, content_type='application/octet-stream')
        resp['Content-Length'] = os.path.getsize(attachment.upload.path)
        resp['Content-Disposition'] = 'filename={}'.format(os.path.basename(
            attachment.upload.name.encode('utf-8', 'ignore')
        ))

        return resp
