from django.core.mail import send_mass_mail
from django.conf import settings
from django.template.loader import render_to_string
from rest_framework import exceptions, mixins, viewsets

from api_v3.models import Action, Comment, Profile, Ticket
from api_v3.misc.queue import queue
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

    def filter_queryset(self, queryset):
        """Patch filtering method to use the search implementation."""
        filters = self.extract_filter_params(self.request)
        filtered = super(TicketsEndpoint, self).filter_queryset(queryset)

        if filters.get('search'):
            filtered = Ticket.search_for(filters.get('search'), filtered)

        return filtered

    def perform_create(self, serializer):
        """Make sure every new ticket is linked to current user."""
        # Add by default any country to the countries list
        country = serializer.initial_data['country']
        countries = serializer.initial_data['countries']

        if country and (country not in countries):
            countries.append(country)
            countries = list(set(countries))

        ticket = serializer.save(
            requester=self.request.user, countries=countries
        )

        Action.objects.create(
            actor=self.request.user, target=ticket,
            verb=self.action_name())

        self.email_notify(ticket.id, self.request.get_host())

        return ticket

    def perform_update(self, serializer):
        """Allow only super users and ticket authors to update the ticket.

        There're undocumented attributes: ``reopen_reason`` and
        ``pending_reason``. Passing these attributes will create and attach a
        comment with it's value to the relevant activity.
        """
        instance = serializer.instance

        if (not self.request.user.is_superuser) and (
            self.request.user not in instance.users.all()
        ) and (
            self.request.user != instance.requester
        ):
            raise exceptions.NotFound()

        comment = None
        status = serializer.validated_data.get('status')
        status_changed = instance.status != status
        instance.countries = list(set(instance.countries))

        if status_changed:
            verb = '{}:status_{}'.format(self.action_name(), status)
        else:
            verb = self.action_name()

        ticket = serializer.save()
        init_data = serializer.initial_data

        if init_data.get('reopen_reason'):
            verb = '{}:reopen'.format(self.action_name())
            self.email_notify(
                ticket.id,
                self.request.get_host(),
                template='mail/ticket_reopened.txt'
            )
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

    @staticmethod
    @queue.task()
    def email_notify(ticket_id, request_host, template=None):
        """Sends an email to editors about the new ticket."""
        ticket = Ticket.objects.get(pk=ticket_id)
        emails = []
        template = template or 'mail/ticket_created.txt'
        subject = TicketsEndpoint.EMAIL_SUBJECT.format(ticket.id)

        if template == 'mail/ticket_created.txt':
            users = Profile.objects.filter(is_superuser=True, is_active=True)
        else:
            users = ticket.users

        for user in users:
            emails.append([
                subject,
                render_to_string(template, {
                    'ticket': ticket,
                    'name': user.display_name,
                    'request_host': request_host,
                    'site_name': settings.SITE_NAME
                }),
                settings.DEFAULT_FROM_EMAIL,
                [user.email]
            ])

        send_mass_mail(emails, fail_silently=True)
