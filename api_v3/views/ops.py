from rest_framework import response, viewsets, permissions

from api_v3.management.commands.email_ticket_digest import Command


class OpsEndpoint(viewsets.ViewSet):
    """Triggers internal operations."""

    permission_classes = (permissions.AllowAny,)

    def retrieve(self, request, pk=None):
        data = {'operation': None}

        if pk == 'email_ticket_digest':
            cmd = Command()
            status = cmd.handle(
                request_host=self.request.get_host()
            )
            data['operation'] = pk
            data['status'] = status

        return response.Response(data)
