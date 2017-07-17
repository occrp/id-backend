from django.db.models import Q, F, Func, Value
from rest_framework import(
    response, viewsets, mixins, serializers, exceptions)

from .support import JSONApiEndpoint
from .models import Profile, Ticket, Action, Attachment, Comment, Responder
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


class TicketsEndpoint(
        JSONApiEndpoint,
        mixins.CreateModelMixin,
        mixins.UpdateModelMixin,
        viewsets.ReadOnlyModelViewSet):

    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer
    ordering_fields = ('created_at', 'deadline_at')
    filter_fields = (
        'created_at',
        'deadline_at',
        'status',
        'requester',
        'responders'
    )

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

        Action.objects.create(
            actor=self.request.user, target=ticket,
            verb=self.action_name())
        return ticket

    def perform_update(self, serializer):
        """Allow only super users and ticket authors to update the ticket."""
        if not self.request.user.is_superuser:
            raise exceptions.NotFound()

        status = serializer.validated_data.get('status')

        if serializer.instance.status != status:
            verb = '{}:status_{}'.format(self.action_name(), status)
        else:
            verb = self.action_name()

        ticket = serializer.save()

        return Action.objects.create(
            actor=self.request.user, target=ticket, verb=verb)


class ProfilesEndpoint(
        JSONApiEndpoint,
        mixins.UpdateModelMixin,
        viewsets.ReadOnlyModelViewSet):

    queryset = Profile.objects.filter(
        Q(is_staff=True) | Q(is_superuser=True)
    ).all()

    serializer_class = ProfileSerializer

    def perform_update(self, serializer):
        """Allow users to update only own profile."""

        if self.request.user != serializer.instance:
            raise exceptions.NotFound()

        settings = serializer.validated_data.get('settings') or {}
        serializer.instance.settings = serializer.instance.settings or {}
        serializer.instance.settings.update(settings)
        serializer.instance.save()

        return serializer

    def get_queryset(self):
        filters = self.extract_filter_params(self.request)

        if not filters.get('name'):
            return self.queryset
        else:
            return self.queryset.annotate(
                name=Func(
                    Value(' '), F('first_name'), F('last_name'),
                    function='concat_ws'
                )
            ).filter(name__icontains=filters.pop('name'))


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
        ticket = Ticket.filter_by_user(self.request.user).filter(
            id=getattr(serializer.validated_data['ticket'], 'id', None)
        ).first()

        if not ticket and not self.request.user.is_superuser:
            raise serializers.ValidationError(
                [{'data/attributes/ticket': 'Ticket not found.'}]
            )
        else:
            attachment = serializer.save(user=self.request.user)

            return Action.objects.create(
                actor=self.request.user, target=ticket, action=attachment,
                verb=self.action_name())


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

            return Action.objects.create(
                actor=self.request.user, target=ticket, action=comment,
                verb=self.action_name())


class RespondersEndpoint(
        JSONApiEndpoint,
        mixins.CreateModelMixin,
        mixins.DestroyModelMixin,
        viewsets.ReadOnlyModelViewSet):
    """Ticket responders endpoint.

    Use it to add or remove ticket responders.
    """

    queryset = Responder.objects.all()
    serializer_class = ResponderSerializer

    def get_queryset(self):
        queryset = super(RespondersEndpoint, self).get_queryset()

        if self.request.user.is_superuser:
            return queryset

        # If this is anonymous, for some reason DRF evaluates the
        # authentication after the queryset
        if not self.request.user.is_active:
            return queryset.none()

        return Responder.filter_by_user(self.request.user, queryset)

    def perform_create(self, serializer):
        """Make sure only super user can add responders."""
        if not self.request.user.is_superuser:
            raise serializers.ValidationError(
                [{'data/attributes/ticket': 'Ticket not found.'}]
            )

        responder = serializer.save()

        return Action.objects.create(
            actor=self.request.user, target=responder.ticket,
            action=responder.user, verb=self.action_name())

    def perform_destroy(self, instance):
        """Make sure only super user or user himself can remove responders."""
        if not self.request.user.is_superuser and (
                self.request.user != instance.user):
            raise exceptions.NotFound()

        activity = Action.objects.create(
            actor=self.request.user, target=instance.ticket,
            action=instance.user, verb=self.action_name())

        instance.delete()

        return activity
