import logging

from django.core.management.base import BaseCommand
from django.conf import settings
from django.db import connection
from api_v3.models.queue_job import QueueJob, queue


class Command(BaseCommand):
    help = 'Starts the jobs queue'

    def add_arguments(self, parser):
        parser.add_argument(
            '--inspect',
            help='Shows the queue stats.'
        )
        parser.add_argument(
            '--clean',
            help='Removes processed jobs.'
        )

    def handle(self, *args, **options):
        """Runs the queue."""
        if options['clean']:
            deleted = QueueJob.objects.filter(
                dequeued_at__isnull=False
            ).delete()

            self.stdout.write('Removed {0} jobs.'.format(deleted[0]))

            return None

        if options['inspect']:
            for qj in QueueJob.objects.filter(dequeued_at=None).values():
                for colname, colvalue in qj.items():
                    row = '{0}\t{1}'.format(colname, colvalue)
                    self.stdout.write(row.expandtabs(15))
                self.stdout.write('⬛' * 15)

            return None

        logger = logging.getLogger('pq')

        logger.debug('Starting background processing...')

        if not settings.DEBUG:
            logger.setLevel(logging.WARNING)

        queue.work()
