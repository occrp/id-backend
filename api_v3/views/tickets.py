from datetime import datetime

from django.core.mail import send_mass_mail
from django.conf import settings
from django.template.loader import render_to_string
from rest_framework import exceptions, mixins, serializers, viewsets

from api_v3.models import Action, Comment, Profile, Ticket
from api_v3.serializers import TicketSerializer
from .support import JSONApiEndpoint


class TicketsEndpoint(
        JSONApiEndpoint,
        mixins.CreateModelMixin,
        mixins.UpdateModelMixin,
        viewsets.ReadOnlyModelViewSet):

    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer
    ordering_fields = ('created_at', 'deadline_at')
    filter_fields = {
        'created_at': ['range'],
        'deadline_at': ['range'],
        'status': ['in'],
        'kind': ['exact'],
        'country': ['exact'],
        'requester': ['exact'],
        'responders__user': ['exact', 'isnull']
    }

    EMAIL_SUBJECT = 'A new ticket was requested, ID: {}'

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

        self.email_notify(ticket)

        return ticket

    def perform_update(self, serializer):
        """Allow only super users and ticket authors to update the ticket.

        There're undocumented attributes: ``reopen_reason`` and
        ``pending_reason``. Passing these attributes will create and attach a
        comment with it's value to the relevant activity.
        """
        if (not self.request.user.is_superuser) and (
            self.request.user not in serializer.instance.users.all()
        ) and (
            self.request.user != serializer.instance.requester
        ):
            raise exceptions.NotFound()

        comment = None
        status = serializer.validated_data.get('status')
        deadline_at = serializer.validated_data.get('deadline_at')

        if status == Ticket.STATUSES[3][0]:
            # If we're closing the ticket, we do not check for the deadline.
            pass
        elif deadline_at and deadline_at < datetime.utcnow():
            raise serializers.ValidationError([{
                'data/attributes/deadline_at':
                'The date can not be in the past.'
            }])

        if serializer.instance.status != status:
            verb = '{}:status_{}'.format(self.action_name(), status)
        else:
            verb = self.action_name()

        ticket = serializer.save()
        init_data = serializer.initial_data

        if init_data.get('reopen_reason'):
            verb = '{}:reopen'.format(self.action_name())
        elif init_data.get('pending_reason'):
            verb = '{}:pending'.format(self.action_name())

        if init_data.get('reopen_reason') or init_data.get('pending_reason'):
            comment = Comment.objects.create(
                ticket=ticket,
                user=self.request.user,
                body=(
                    init_data.get('reopen_reason') or
                    init_data.get('pending_reason')
                )
            )

        return Action.objects.create(
            actor=self.request.user, target=ticket, verb=verb, action=comment)

    def email_notify(self, ticket):
        """Sends an email to editors about the new ticket."""
        emails = []
        subject = self.EMAIL_SUBJECT.format(ticket.id)
        users = Profile.objects.filter(is_superuser=True, is_active=True)

        for user in users:
            emails.append([
                subject,
                render_to_string(
                    'mail/ticket_created.txt', {
                        'ticket': ticket,
                        'name': user.display_name,
                        'request_host': self.request.get_host()
                    }
                ),
                settings.DEFAULT_FROM_EMAIL,
                [user.email]
            ])

        return send_mass_mail(emails, fail_silently=True)
