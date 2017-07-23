from datetime import datetime
from collections import defaultdict

from django.db import models
from django.core.mail import send_mass_mail
from django.core.management.base import BaseCommand
from django.template.loader import render_to_string

from api_v3.models import Ticket, Action
from settings.settings import DEFAULT_FROM_EMAIL


class Command(BaseCommand):
    help = 'Sends relevant ticket notifications'

    SUBJECT = 'Daily digest for your ID tickets'
    # Email item template. Example:
    #   (01.12.1987 22:01): John updated the status to ticket ID: 99
    ITEM_TEMPLATE = '({date}): {name} {action} {thing} to ticket ID: {ticket}'

    def handle(self, *args, **options):
        """Runs the digest for tickets."""
        user_digests = {}
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
                user_digests[user.id] = user_digests.get(user.id) or {
                    'user': user,
                    'digests': digest
                }
                user_digests[user.id]['digests'] += digest

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

        self.stdout.write(color('Sent {} notifications.'.format(count)))

        return status, count

    def digest(self, ticket):
        """Generates a digest for a ticket."""
        actions = Action.objects.filter(
            target_object_id=str(ticket.id),
            timestamp__gte=(ticket.sent_notifications_at or datetime.min)
        )
        return filter(None, map(self.generate_text, actions))

    def email(self, user_digests):
        """Generates and emails the user digests."""
        emails = []

        for _, user_digest in user_digests.items():
            emails.append([
                self.SUBJECT,
                render_to_string('mail/ticket_digest.txt', user_digest),
                DEFAULT_FROM_EMAIL,
                [user_digest['user'].email]
            ])

        return send_mass_mail(emails, fail_silently=True), len(user_digests)

    def generate_text(self, action):
        """Generates a human readable version of the ticket activity."""
        verb = action.verb.split(':')
        data = {
            'name': action.actor.display_name,
            'ticket': action.target.id,
            'thing': verb[0],
            'date': action.timestamp.strftime('%x %X'),
            'action': 'added a'
        }

        # If it's a ticket update
        if len(verb) == 3:
            attr_name, attr_val = verb[2].split('_')
            data['action'] = 'updated'
            data['thing'] = '{} to {}'.format(attr_name, attr_val)
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
