from rest_framework import response, viewsets, mixins, serializers, exceptions

from .support import JSONApiEndpoint
from .models import Profile, Ticket, Action, Attachment, Comment
from .serializers import(
    ProfileSerializer,
    TicketSerializer,
    AttachmentSerializer,
    ActionSerializer,
    CommentSerializer,
    ResponderSerializer
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
            return queryset

        # If this is anonymous, for some reason DRF evaluates the
        # authentication after the queryset
        if not self.request.user.is_active:
            return queryset.none()

        return Ticket.filter_by_user(self.request.user, queryset)

    def perform_create(self, serializer):
        """Make sure every new ticket is linked to current user."""
        ticket = serializer.save(requester=self.request.user)
        activity = Action.objects.create(
            actor=self.request.user, target=ticket, verb=self.request.method)


class UsersEndpoint(JSONApiEndpoint, viewsets.ReadOnlyModelViewSet):
    queryset = Profile.objects.filter(is_staff=True, is_superuser=True).all()
    serializer_class = ProfileSerializer


class ActivitiesEndpoint(JSONApiEndpoint, viewsets.ReadOnlyModelViewSet):
    queryset = Action.objects.all()
    serializer_class = ActionSerializer

    def get_queryset(self):
        queryset = super(ActivitiesEndpoint, self).get_queryset()

        if self.request.user.is_superuser:
            return queryset

        # If this is anonymous, for some reason DRF evaluates the
        # authentication after the queryset
        if not self.request.user.is_active:
            return queryset.none()

        user_ticket_ids = Ticket.filter_by_user(
            self.request.user).values_list('id', flat=True)
        return Action.objects.filter(
            target_object_id__in=map(str, user_ticket_ids))


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

        return Attachment.filter_by_user(self.request.user, queryset)

    def perform_create(self, serializer):
        """Make sure every new attachment is linked to current user."""
        ticket = Ticket.filter_by_user(self.requester.user).filter(
            id=getattr(serializer.validated_data['ticket'], 'id', None)
        ).first()

        if not ticket and not self.request.user.is_superuser:
            raise serializers.ValidationError(
                [{'data/attributes/ticket': 'Ticket not found.'}]
            )
        else:
            attachment = serializer.save(user=self.request.user)
            activity = Action.objects.create(
                actor=self.request.user, target=ticket, action=attachment,
                verb=self.request.method)
            return attachment


class CommentsEndpoint(
        JSONApiEndpoint,
        mixins.CreateModelMixin,
        viewsets.ReadOnlyModelViewSet):

    queryset = Comment.objects.all()
    serializer_class = CommentSerializer

    def get_queryset(self):
        queryset = super(CommentsEndpoint, self).get_queryset()

        if self.request.user.is_superuser:
            return queryset

        # If this is anonymous, for some reason DRF evaluates the
        # authentication after the queryset
        if not self.request.user.is_active:
            return queryset.none()

        return Comment.filter_by_user(self.request.user, queryset)

    def perform_create(self, serializer):
        """Make sure every new attachment is linked to current user."""
        ticket = Ticket.filter_by_user(self.request.user).filter(
            id=getattr(serializer.validated_data['ticket'], 'id', None)
        ).first()

        if not ticket and not self.request.user.is_superuser:
            raise serializers.ValidationError(
                [{'data/attributes/ticket': 'Ticket not found.'}]
            )
        else:
            comment = serializer.save(user=self.request.user)
            activity = Action.objects.create(
                actor=self.request.user, target=ticket, action=comment,
                verb=self.request.method)


class RespondersEndpoint(
        JSONApiEndpoint,
        mixins.CreateModelMixin,
        mixins.DestroyModelMixin,
        viewsets.GenericViewSet):
    """Ticket responders endpoint.

    Use it to add or remove ticket responders.
    """

    queryset = Ticket.responders.through.objects.all()
    serializer_class = ResponderSerializer

    def perform_create(self, serializer):
        """Make sure only super user can add responders."""
        if not self.request.user.is_superuser:
            raise serializers.ValidationError(
                [{'data/attributes/ticket': 'Ticket not found.'}]
            )

        responder = serializer.save()
        activity = Action.objects.create(
            actor=self.request.user, target=responder.ticket,
            action=responder.profile, verb=self.request.method)

    def perform_delete(self, instance):
        """Make sure only super user or user himself can remove responders."""
        if not self.request.user.is_superuser or (
                self.request.user != instance.profile):
            raise exceptions.NotFound()

        activity = Action.objects.create(
            actor=self.request.user, target=responder.ticket,
            action=responder.profile, verb=self.request.method)

        instance.delete()

        return activity
