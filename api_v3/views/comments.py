from django.conf import settings
from django.core.mail import send_mass_mail
from django.template.loader import render_to_string
from rest_framework import mixins, serializers, viewsets

from api_v3.models import Action, Comment, Ticket
from api_v3.serializers import CommentSerializer
from .support import JSONApiEndpoint


class CommentsEndpoint(
        JSONApiEndpoint,
        mixins.CreateModelMixin,
        viewsets.ReadOnlyModelViewSet):

    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    EMAIL_SUBJECT = 'A new comment for ticket ID: {}'

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
        """Make sure every new comment is linked to current user."""
        ticket = Ticket.filter_by_user(self.request.user).filter(
            id=getattr(serializer.validated_data['ticket'], 'id', None)
        ).first()

        if not ticket and not self.request.user.is_superuser:
            raise serializers.ValidationError(
                [{'data/attributes/ticket': 'Ticket not found.'}]
            )
        else:
            comment = serializer.save(user=self.request.user)

            Action.objects.create(
                action=comment,
                target=comment.ticket,
                actor=self.request.user,
                verb=self.action_name()
            )

            self.email_notify(comment)

            return comment

    def email_notify(self, comment):
        """Sends an email to ticket users about the new comment."""
        emails = []
        subject = self.EMAIL_SUBJECT.format(comment.ticket.id)
        users = list(comment.ticket.users.all()) + [comment.ticket.requester]
        request_host = ''

        if hasattr(self, 'request'):
            request_host = self.request.get_host()

        for user in users:

            if user == comment.user:
                continue

            emails.append([
                subject,
                render_to_string(
                    'mail/ticket_comment.txt', {
                        'comment': comment,
                        'name': user.display_name,
                        'request_host': request_host
                    }
                ),
                settings.DEFAULT_FROM_EMAIL,
                [user.email]
            ])

        return send_mass_mail(emails, fail_silently=True), emails
