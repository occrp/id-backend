from django.core.mail import send_mass_mail
from django.conf import settings
from django.template.loader import render_to_string
from rest_framework import exceptions, mixins, serializers, viewsets

from api_v3.models import Action, Responder, Ticket
from api_v3.misc.queue import queue
from api_v3.serializers import ResponderSerializer
from .support import JSONApiEndpoint


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

    EMAIL_SUBJECT = 'You were added to the ticket ID: {}'

    def get_queryset(self):
        queryset = super(RespondersEndpoint, self).get_queryset()

        if self.request.user.is_superuser:
            return queryset

        # If this is anonymous, for some reason DRF evaluates the
        # authentication after the queryset
        if not self.request.user.is_active:
            return queryset.none()

        return Responder.filter_by_user(self.request.user, queryset).distinct()

    def perform_create(self, serializer):
        """Make sure only super user can add responders."""
        if not self.request.user.is_superuser:
            raise serializers.ValidationError(
                [{'attributes/ticket': {'detail': 'Ticket not found.'}}]
            )

        responder = serializer.save()
        # Set the next-in-workflow ticket status
        responder.ticket.status = Ticket.STATUSES[1][0]
        responder.ticket.save()

        action = Action.objects.create(
            actor=self.request.user, target=responder.ticket,
            action=responder.user, verb=self.action_name())

        self.email_notify(action.id, self.request.get_host())

        return responder

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

    @staticmethod
    @queue.task()
    def email_notify(_job_id, action_id, request_host):
        """Sends an email to the responder about the new ticket."""
        activity = Action.objects.get(id=action_id)
        subject = RespondersEndpoint.EMAIL_SUBJECT.format(activity.target.id)
        emails = [
            [
                subject,
                render_to_string(
                    'mail/responder_created.txt', {
                        'ticket': activity.target,
                        'name': activity.action.display_name,
                        'request_host': request_host,
                        'site_name': settings.SITE_NAME
                    }
                ),
                settings.DEFAULT_FROM_EMAIL,
                [activity.action.email]
            ]
        ]

        return send_mass_mail(emails)
