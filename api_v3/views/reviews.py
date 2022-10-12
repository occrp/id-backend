from django.conf import settings
from django.core.mail import send_mass_mail
from django.template.loader import render_to_string
from rest_framework import mixins, serializers, viewsets, permissions

from api_v3.models import Action, Review, Ticket
from api_v3.misc.queue import queue
from api_v3.serializers import ReviewSerializer
from .support import JSONApiEndpoint


class ReviewsEndpoint(
        JSONApiEndpoint,
        mixins.CreateModelMixin,
        viewsets.GenericViewSet):

    permission_classes = (permissions.AllowAny,)
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    EMAIL_SUBJECT = 'Please review ticket ID: {}'

    def get_queryset(self):
        queryset = super(ReviewsEndpoint, self).get_queryset()

        if self.request.user.is_superuser:
            return queryset

        return queryset.none()

    def perform_create(self, serializer):
        """Make sure every new comment is linked to current user."""
        init_data = serializer.initial_data
        ticket = Review.ticket_from_token(init_data.get('token'))

        if not ticket:
            raise serializers.ValidationError(
                [{'attributes/ticket': {'detail': 'Ticket not found.'}}]
            )
        else:
            review = serializer.save(ticket=ticket)

            Action.objects.create(
                action=review,
                target=ticket,
                verb=self.action_name()
            )

            return review

    @staticmethod
    @queue.task(schedule_at='1d')
    def email_notify(_job_id, ticket_id, request_host):
        """Sends an email to ticket users to leave a review."""
        if settings.REVIEWS_DISABLED:
            return

        emails = []
        ticket = Ticket.objects.get(pk=ticket_id)
        subject = ReviewsEndpoint.EMAIL_SUBJECT.format(ticket_id)

        # If the ticket status changed in the meantime, do not request reviews.
        if ticket.status != Ticket.STATUSES[3][0]:
            return None

        to_notify = [ticket.requester.__dict__]
        to_notify += (
            ticket.subscribers.filter(email__isnull=False).distinct('email')
            .values('email')
        )[:]

        for entry in to_notify:
            emails.append([
                subject,
                render_to_string(
                    'mail/review_request.txt', {
                        'ticket': ticket,
                        'token': Review.ticket_to_token(ticket),
                        'days_to_respond': Review.MAX_DAYS_TO_RESPOND,
                        'request_host': request_host,
                        'site_name': settings.SITE_NAME
                    }
                ),
                settings.DEFAULT_FROM_EMAIL,
                [entry['email']]
            ])

        return send_mass_mail(emails), emails
