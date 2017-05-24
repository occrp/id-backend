from rest_framework import generics, response, viewsets


from .support import JSONApiEndpoint
from .models import Profile, Ticket, Notification, Attachment
from .serializers import(
    ProfileSerializer,
    TicketSerializer,
    NotificationSerializer,
    AttachmentSerializer
)


class SessionEndpoint(generics.GenericAPIView):
    serializer_class = ProfileSerializer

    def get(self, request, *args, **kwargs):
        serializer = self.get_serializer(request.user)
        return response.Response(serializer.data)


class TicketsEndpoint(JSONApiEndpoint, viewsets.ModelViewSet):
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer


class UsersEndpoint(JSONApiEndpoint, viewsets.ModelViewSet):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer


class NotificationsEndpoint(JSONApiEndpoint, viewsets.ModelViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer


class AttachmentsEndpoint(JSONApiEndpoint, viewsets.ModelViewSet):
    queryset = Attachment.objects.all()
    serializer_class = AttachmentSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
