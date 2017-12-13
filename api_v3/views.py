from collections import namedtuple
from datetime import datetime
import os.path

from django.db.models import Q, F, Func, Value, Count, Avg
from django.db.models.functions import Trunc
from django.core.mail import send_mass_mail
from django.template.loader import render_to_string
from django.http import FileResponse
from rest_framework import(
    response, viewsets, mixins, serializers, exceptions, permissions)

from settings.settings import DEFAULT_FROM_EMAIL
from .support import JSONApiEndpoint
from .models import Profile, Ticket, Action, Attachment, Comment, Responder
from .management.commands.email_ticket_digest import Command
from .serializers import(
    ProfileSerializer,
    TicketSerializer,
    AttachmentSerializer,
    ActionSerializer,
    CommentSerializer,
    ResponderSerializer,
    TicketStatSerializer
)


class SessionEndpoint(viewsets.GenericViewSet):
    serializer_class = ProfileSerializer

    def list(self, request, *args, **kwargs):
        serializer = self.get_serializer(request.user)
        return response.Response(serializer.data)


class OpsEndpoint(viewsets.ViewSet):
    """Triggers internal operations."""

    permission_classes = (permissions.AllowAny,)

    def retrieve(self, request, pk=None):
        data = {'operation': None}

        if pk == 'email_ticket_digest':
            cmd = Command()
            status = cmd.handle(
                request_host=self.request.get_host()
            )
            data['operation'] = pk
            data['status'] = status

        return response.Response(data)


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

        deadline_at = serializer.validated_data.get('deadline_at')

        if deadline_at and deadline_at < datetime.utcnow():
            raise serializers.ValidationError([{
                'data/attributes/deadline_at':
                'The date can not be in the past.'
            }])

        comment = None
        status = serializer.validated_data.get('status')

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
                DEFAULT_FROM_EMAIL,
                [user.email]
            ])

        return send_mass_mail(emails, fail_silently=True)


class ProfilesEndpoint(
        JSONApiEndpoint,
        mixins.UpdateModelMixin,
        viewsets.ReadOnlyModelViewSet):

    queryset = Profile.objects.filter(Q(is_active=True)).all()

    serializer_class = ProfileSerializer
    filter_fields = ('is_superuser', 'is_staff')

    def perform_update(self, serializer):
        """Allow users to update only own profile."""

        if self.request.user != serializer.instance:
            raise exceptions.NotFound()

        serializer.instance.bio = serializer.validated_data.get('bio')
        serializer.instance.save()

        return serializer

    def get_queryset(self):
        filters = self.extract_filter_params(self.request)

        # If not a super-user, do not allow access
        if self.request.user and not self.request.user.is_superuser:
            return self.queryset.filter(pk=self.request.user.pk)

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
    ordering_fields = ('timestamp',)
    ordering = ('-timestamp',)
    filter_fields = {
        'timestamp': ['range'],
        'target_object_id': ['exact'],
        'actor_object_id': ['exact']
    }

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

            Action.objects.create(
                action=attachment,
                actor=self.request.user,
                target=attachment.ticket,
                verb=self.action_name()
            )

            return attachment


class DownloadEndpoint(viewsets.ViewSet):

    permission_classes = (permissions.IsAuthenticated,)

    def retrieve(self, request, pk=None):
        user_ticket_ids = Ticket.filter_by_user(
            self.request.user).values_list('id', flat=True)

        if self.request.user.is_superuser:
            attachment = Attachment.objects.get(id=pk)
        else:
            attachment = Attachment.objects.filter(
                id=pk, ticket__in=user_ticket_ids).first()

        if not attachment or not attachment.upload:
            raise exceptions.NotFound()

        resp = FileResponse(
            attachment.upload.file, content_type='application/octet-stream')
        resp['Content-Length'] = os.path.getsize(attachment.upload.path)
        resp['Content-Disposition'] = 'filename={}'.format(os.path.basename(
            attachment.upload.name.encode('utf-8', 'ignore')
        ))

        return resp


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
                DEFAULT_FROM_EMAIL,
                [user.email]
            ])

        return send_mass_mail(emails, fail_silently=True), emails


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

        return Responder.filter_by_user(self.request.user, queryset)

    def perform_create(self, serializer):
        """Make sure only super user can add responders."""
        if not self.request.user.is_superuser:
            raise serializers.ValidationError(
                [{'data/attributes/ticket': 'Ticket not found.'}]
            )

        responder = serializer.save()
        # Set the next-in-workflow ticket status
        responder.ticket.status = Ticket.STATUSES[1][0]
        responder.ticket.save()

        action = Action.objects.create(
            actor=self.request.user, target=responder.ticket,
            action=responder.user, verb=self.action_name())

        self.email_notify(action)

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

    def email_notify(self, activity):
        """Sends an email to the responder about the new ticket."""
        subject = self.EMAIL_SUBJECT.format(activity.target.id)
        emails = [
            [
                subject,
                render_to_string(
                    'mail/responder_created.txt', {
                        'ticket': activity.target,
                        'name': activity.action.display_name,
                        'request_host': self.request.get_host()
                    }
                ),
                DEFAULT_FROM_EMAIL,
                [activity.action.email]
            ]
        ]

        return send_mass_mail(emails, fail_silently=True)


class TicketStatsEndpoint(JSONApiEndpoint, viewsets.ReadOnlyModelViewSet):
    queryset = Ticket.objects.all()
    serializer_class = TicketStatSerializer
    filter_fields = {
        'created_at': ['range'],
        'status': ['in'],
        'kind': ['exact'],
        'country': ['exact'],
        'responders__user': ['exact', 'isnull']
    }

    class TicketStat(dict):
        __getattr__ = dict.__getitem__
        __setattr__ = dict.__setitem__

    def get_queryset(self):
        queryset = super(TicketStatsEndpoint, self).get_queryset()

        if not self.request.user.is_superuser:
            return queryset.none()

        queryset = queryset.annotate(
            date=Trunc('created_at', 'month'),
            count=Count('id'),
            ticket_status=F('status'),
            avg_time=Avg((F('updated_at') - F('created_at')))
        ).values('date', 'count', 'ticket_status', 'avg_time')

        # Do not group by all the aggregations
        queryset.query.group_by = queryset.query.group_by[-2:]

        return queryset

    def get_serializer(self, queryset, *args, **kwargs):
        profile = None
        params = self.extract_filter_params(self.request)

        if params.get('responders__user'):
            profile = Profile.objects.get(id=params.get('responders__user'))

        stats = map(
            lambda s: self.TicketStat(s, profile=profile, params=params, pk=None),
            list(queryset)
        )

        serializer = super(TicketStatsEndpoint, self).get_serializer(
            stats, *args, **kwargs)

        return response.Response(serializer.data)
