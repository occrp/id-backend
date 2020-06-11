from datetime import datetime

from django.db import models
from django.conf import settings
from django.core.mail import send_mass_mail
from django.core.management.base import BaseCommand
from django.template.loader import render_to_string

from api_v3.models import Ticket, Action
from api_v3.misc.queue import queue


class Command(BaseCommand):
    help = 'Sends relevant ticket notifications'

    # Days left until deadline
    UPCOMING_DAYS_LEFT = [-1, 0, 1]

    SUBJECT = 'Daily digest for your ID tickets'
    # Email item template. Example:
    #   (01.12.1987 22:01): John updated the status to ticket ID: 99
    ITEM_TEMPLATE = (
        '({date}): {name} {action} {thing} {prep} ticket '
        'https://{request_host}/tickets/view/{ticket}'
    )

    @staticmethod
    @queue.task(schedule_at='1d')
    def schedule(request_host):
        """Task job handler.

        Run it manually once and it will reschedule itself on a daily basis.
        """
        Command().handle(request_host=request_host)

        # Reschedule...
        Command.schedule(request_host)

    def add_arguments(self, parser):
        parser.add_argument('request_host', help='Hostname to use in emails.')

    def handle(self, *args, **options):
        """Runs the digest for tickets."""
        user_digests = {}
        self.request_host = options.get('request_host')
        tickets = Ticket.objects.filter(
            models.Q(
                sent_notifications_at__gte=models.Func(function='now')
            ) | models.Q(
                sent_notifications_at=None
            )
        )

        self.stdout.write('Processing {} tickets.'.format(tickets.count()))

        for ticket in tickets:
            digest = self.digest(ticket)

            if not digest:
                continue

            for user in (list(ticket.users.all()) + [ticket.requester]):
                upcoming_in = 'never'
                user_digests[user.id] = user_digests.get(user.id) or {
                    'request_host': self.request_host,
                    'site_name': settings.SITE_NAME,
                    'user': user,
                    'digests': [],
                    'upcoming': set()
                }

                user_digests[user.id]['digests'] += digest

                if ticket.deadline_at and user != ticket.requester:
                    upcoming_in = (ticket.deadline_at - datetime.utcnow()).days

                if upcoming_in in self.UPCOMING_DAYS_LEFT:
                    user_digests[user.id]['upcoming'].add(ticket)

            ticket.sent_notifications_at = datetime.utcnow()
            ticket.save()

        if user_digests:
            status, count = self.email(user_digests)
        else:
            status, count = True, 0

        if status:
            color = self.style.SUCCESS
        else:
            color = self.style.ERROR

        return color('Sent {} notifications.'.format(count))

    def digest(self, ticket):
        """Generates a digest for a ticket."""
        actions = Action.objects.filter(
            target_object_id=str(ticket.id),
            timestamp__gte=(ticket.sent_notifications_at or datetime.min)
        )
        return [_f for _f in list(map(self.generate_text, actions)) if _f]

    def email(self, user_digests):
        """Generates and emails the user digests."""
        emails = []

        for _, user_digest in list(user_digests.items()):
            emails.append([
                self.SUBJECT,
                render_to_string(
                    'mail/ticket_digest.txt',
                    user_digest
                ),
                settings.DEFAULT_FROM_EMAIL,
                [user_digest['user'].email]
            ])

        return send_mass_mail(emails), len(user_digests)

    def generate_text(self, action):
        """Generates a human readable version of the ticket activity."""
        verb = action.verb.split(':')
        data = {
            'name': action.actor.display_name,
            'request_host': self.request_host,
            'ticket': action.target.id,
            'thing': verb[0],
            'prep': 'to',
            'date': action.timestamp.strftime('%x %X'),
            'action': 'added a'
        }

        # If it's a ticket update
        if len(verb) == 3 and '_' in verb[2]:
            attr_name, attr_val = verb[2].split('_')
            data['action'] = 'updated'
            data['thing'] = '{} to {}'.format(attr_name, attr_val)
        elif len(verb) == 3 and 'reopen' in verb:
            data['action'] = 'did'
            data['thing'] = 'reopen'
            data['prep'] = 'the'
        elif len(verb) == 3 and 'pending' in verb:
            data['action'] = 'marked'
            data['thing'] = 'pending (waiting for third-party actions)'
            data['prep'] = 'the'
        # If a new attachment was added
        elif data['thing'] == 'attachment':
            data['action'] = 'added an'
        # If a new responder was added
        elif data['thing'] == 'responder':
            data['action'] = 'added'
            data['thing'] = '{} as a responder'.format(
                action.action.display_name)
        # If a ticket was created, do not include in the digest
        elif data['thing'] == 'ticket':
            return None

        return self.ITEM_TEMPLATE.format(**data)
