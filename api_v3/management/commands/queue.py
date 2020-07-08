import logging

from django.core.management.base import BaseCommand
from django.conf import settings
from django.db import connection
from api_v3.misc.queue import queue


class Command(BaseCommand):
    help = 'Starts the jobs queue'

    def add_arguments(self, parser):
        parser.add_argument(
            '--inspect',
            help='If provided will show queue stats.'
        )

    def handle(self, *args, **options):
        """Runs the queue."""
        if options['inspect']:
            with connection.cursor() as cursor:
                cursor.execute('SELECT * FROM %s', (queue.table,))

                for row in cursor:
                    self.stdout.write("\n".join(str(c) for c in row))
                    self.stdout.write("\n~~~\n\n")

            return None

        logger = logging.getLogger('pq')

        logger.debug('Starting background processing...')

        if not settings.DEBUG:
            logger.setLevel(logging.WARNING)

        queue.work()
