from django.core.mail import send_mass_mail
from django.conf import settings
from django.template.loader import render_to_string
from rest_framework import exceptions, mixins, serializers, viewsets

from api_v3.models import Action, Subscriber, Profile
from api_v3.serializers import SubscriberSerializer
from .support import JSONApiEndpoint


class SubscribersEndpoint(
        JSONApiEndpoint,
        mixins.CreateModelMixin,
        mixins.DestroyModelMixin,
        viewsets.ReadOnlyModelViewSet):
    """Ticket subscribers endpoint.

    Use it to add or remove ticket subscribers.
    """

    queryset = Subscriber.objects.all()
    serializer_class = SubscriberSerializer

    EMAIL_SUBJECT = 'You were subscribed to the ticket ID: {}'

    def get_queryset(self):
        queryset = super(SubscribersEndpoint, self).get_queryset()

        if self.request.user.is_superuser:
            return queryset

        # If this is anonymous, for some reason DRF evaluates the
        # authentication after the queryset
        if not self.request.user.is_active:
            return queryset.none()

        return Subscriber.filter_by_user(self.request.user, queryset).distinct()

    def create(self, request, *args, **kwargs):
        """Validate user before it hits the serializer."""
        email = request.data.pop('email', None)
        subscriber_user = Profile.objects.filter(email=email).first()

        if subscriber_user:
            request.data['user'] = {}
            request.data['user']['id'] = subscriber_user.id
            request.data['user']['type'] = 'profiles'
        else:
            request.data['user'] = None
            request.data['email'] = email

        return super(SubscribersEndpoint, self).create(request, *args, **kwargs)

    def perform_create(self, serializer):
        """Only super user or ticket responders can add subscribers."""
        user = self.request.user
        is_ticket_user = user in serializer.validated_data['ticket'].users

        if not user.is_superuser and not is_ticket_user:
            raise serializers.ValidationError(
                [{'data/attributes/ticket': 'Ticket not found.'}]
            )

        subscriber = serializer.save()

        action = Action.objects.create(
            actor=user, target=subscriber.ticket,
            action=subscriber.user, verb=self.action_name())

        self.email_notify(action, subscriber=subscriber)

        return subscriber

    def perform_destroy(self, instance):
        """Only super user, subscriber or responders can remove subscribers."""
        user = self.request.user
        is_responder = (user in instance.ticket.users.all())
        is_subscriber = (user == instance.user)

        if not user.is_superuser and not is_subscriber and not is_responder:
            raise exceptions.NotFound()

        activity = Action.objects.create(
            actor=user, target=instance.ticket,
            action=instance.user, verb=self.action_name())

        instance.delete()

        return activity

    def email_notify(self, activity, subscriber):
        """Sends an email to the subscriber about the new ticket."""
        subject = self.EMAIL_SUBJECT.format(activity.target.id)
        request_host = ''

        if hasattr(self, 'request'):
            request_host = self.request.get_host()

        emails = [
            [
                subject,
                render_to_string(
                    'mail/subscriber_added.txt', {
                        'ticket': activity.target,
                        'request_host': request_host,
                        'site_name': settings.SITE_NAME,
                        'name': (
                            subscriber.email or subscriber.user.display_name
                        )
                    }
                ),
                settings.DEFAULT_FROM_EMAIL,
                [subscriber.email or subscriber.user.email]
            ]
        ]

        return send_mass_mail(emails, fail_silently=True), emails
