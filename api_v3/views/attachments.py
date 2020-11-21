from rest_framework import viewsets, mixins, serializers, exceptions

from api_v3.models import Action, Ticket, Attachment
from api_v3.serializers import AttachmentSerializer
from .support import JSONApiEndpoint


class AttachmentsEndpoint(
        JSONApiEndpoint,
        mixins.CreateModelMixin,
        mixins.DestroyModelMixin,
        viewsets.ReadOnlyModelViewSet):

    queryset = Attachment.objects.all()
    serializer_class = AttachmentSerializer
    ordering_fields = ('created_at',)
    filter_fields = {
        'created_at': ['range'],
        'ticket': ['exact'],
        'user': ['exact']
    }

    def get_queryset(self):
        queryset = super(AttachmentsEndpoint, self).get_queryset()

        if self.request.user.is_superuser:
            return queryset

        # If this is anonymous, for some reason DRF evaluates the
        # authentication after the queryset
        if not self.request.user.is_active:
            return queryset.none()

        return Attachment.filter_by_user(self.request.user, queryset)

    def perform_create(self, serializer):
        """Make sure every new attachment is linked to current user."""
        ticket = Ticket.filter_by_user(self.request.user).filter(
            id=getattr(serializer.validated_data['ticket'], 'id', None)
        ).first()

        if not ticket and not self.request.user.is_superuser:
            raise serializers.ValidationError(
                [{'attributes/ticket': {'detail': 'Ticket not found.'}}]
            )
        else:
            attachment = serializer.save(user=self.request.user)

            Action.objects.create(
                action=attachment,
                actor=self.request.user,
                target=attachment.ticket,
                verb=self.action_name()
            )

            return attachment

    def perform_destroy(self, instance):
        """Make sure only super user or author can remove the attachment."""
        if not self.request.user.is_superuser and (
                self.request.user != instance.user):
            raise exceptions.NotFound()

        activity = Action.objects.create(
            actor=self.request.user, target=instance.ticket,
            action=instance.user, verb=self.action_name())

        instance.delete()

        return activity
