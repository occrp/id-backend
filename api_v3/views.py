from django.db import models
from rest_framework import generics, response, viewsets, mixins, serializers

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
    queryset = Ticket.objects
    serializer_class = TicketSerializer

    def get_queryset(self):
        queryset = super(TicketsEndpoint, self).get_queryset()

        if self.request.user.is_superuser:
            return super(TicketsEndpoint, self).get_queryset()

        # If this is anonymous, for some reason DRF evaluates the
        # authentication after the queryset
        if not self.request.user.is_active:
            return queryset.none()

        return queryset.filter(
            # Let ticket authors see own tickets
            models.Q(
                requester=self.request.user
            ) |
            # Let ticket responders see subscribed tickets
            models.Q(
                responders=self.request.user
            )
        )

    def perform_create(self, serializer):
        """Make sure every new ticket is linked to current user."""
        serializer.save(requester=self.request.user)


class UsersEndpoint(JSONApiEndpoint, viewsets.ReadOnlyModelViewSet):
    queryset = Profile.objects.filter(is_staff=True, is_superuser=True).all()
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

    def get_queryset(self):
        queryset = super(AttachmentsEndpoint, self).get_queryset()

        if self.request.user.is_superuser:
            return queryset

        # If this is anonymous, for some reason DRF evaluates the
        # authentication after the queryset
        if not self.request.user.is_active:
            return queryset.none()

        return queryset.filter(
            # Let ticket authors see own tickets
            models.Q(
                ticket__requester=self.request.user
            ) |
            # Let ticket responders see subscribed tickets
            models.Q(
                ticket__responders=self.request.user
            )
        )

    def perform_create(self, serializer):
        """Make sure every new attachment is linked to current user."""
        ticket = Ticket.objects.filter(
            # Allow ticket authors to send attachments
            models.Q(
                requester=self.request.user
            ) |
            # Allow ticket responders to send attachments
            models.Q(
                responders=self.request.user
            )
        ).filter(
            id=getattr(serializer.validated_data['ticket'], 'id', None)
        ).first()

        if not ticket and not self.request.user.is_superuser:
            raise serializers.ValidationError(
                [{'data/attributes/ticket': 'Ticket not found.'}]
            )
        else:
            return serializer.save(user=self.request.user)
