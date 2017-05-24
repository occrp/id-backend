from rest_framework import generics, response, viewsets, mixins


from .support import JSONApiEndpoint
from .models import Profile, Ticket, Notification, Attachment
from .serializers import(
    ProfileSerializer,
    TicketSerializer,
    NotificationSerializer,
    AttachmentSerializer
)


class SessionEndpoint(viewsets.GenericViewSet):
    serializer_class = ProfileSerializer

    def list(self, request, *args, **kwargs):
        serializer = self.get_serializer(request.user)
        return response.Response(serializer.data)


class TicketsEndpoint(JSONApiEndpoint, viewsets.ModelViewSet):
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer


class UsersEndpoint(JSONApiEndpoint, viewsets.ReadOnlyModelViewSet):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer


class NotificationsEndpoint(JSONApiEndpoint, viewsets.ReadOnlyModelViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer


class AttachmentsEndpoint(
        JSONApiEndpoint,
        mixins.CreateModelMixin,
        viewsets.ReadOnlyModelViewSet):

    queryset = Attachment.objects.all()
    serializer_class = AttachmentSerializer

    def perform_create(self, serializer):
        """Make sure every new attachment is linked to current user."""
        serializer.save(user=self.request.user)
