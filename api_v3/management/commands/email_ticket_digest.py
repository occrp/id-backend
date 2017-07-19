from datetime import datetime

from django.db import models
from django.core.mail import send_mass_mail
from django.core.management.base import BaseCommand
from django.template.loader import render_to_string

from api_v3.models import Ticket, Action
from settings.settings import DEFAULT_FROM_EMAIL


class Command(BaseCommand):
    help = 'Sends relevant ticket notifications'

    SUBJECT = 'Daily digest for ticket ID: {}'
    # Email item template. Example:
    #   John updated the status to ticket ID: 99
    ITEM_TEMPLATE = '{name} {action} {thing} to ticket ID: {ticket}'

    def handle(self, *args, **options):
        tickets = Ticket.objects.filter(
            models.Q(
                sent_notifications_at__gte=models.Func(function='now')
            ) | models.Q(
                sent_notifications_at=None
            )
        )

        self.stdout.write('Processing {} tickets.'.format(tickets.count()))

        for ticket in tickets:
            mail_status, processed = self.process_ticket(ticket)

            ticket.sent_notifications_at = datetime.utcnow()
            ticket.save()

            if mail_status:
                color = self.style.SUCCESS
            else:
                color = self.style.ERROR

            self.stdout.write(color('Sent {} notifications.'.format(processed)))

    def process_ticket(self, ticket):
        actions = Action.objects.filter(
            target_object_id=str(ticket.id),
            timestamp__gte=(ticket.sent_notifications_at or datetime.min)
        )

        emails = []
        items = map(self.generate_text, actions)
        subject = self.SUBJECT.format(ticket.id)

        for user in (list(ticket.users.all()) + [ticket.requester]):
            emails.append([
                subject,
                render_to_string(
                    'mail/ticket_digest.txt', {
                        'actions': items,
                        'name': user.display_name
                    }
                ),
                DEFAULT_FROM_EMAIL,
                [user.email]
            ])

        return send_mass_mail(emails, fail_silently=True), len(items)

    def generate_text(self, action):
        verb = action.verb.split(':')
        data = {
            'name': action.actor.display_name,
            'ticket': action.target.id,
            'thing': verb[0],
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

        return self.ITEM_TEMPLATE.format(**data)
