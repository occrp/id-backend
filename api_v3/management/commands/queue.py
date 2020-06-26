import logging

from django.core.management.base import BaseCommand
from django.conf import settings
from api_v3.misc.queue import queue


class Command(BaseCommand):
    help = 'Starts the jobs queue'

    def handle(self, *args, **options):
        """Runs the queue."""
        logger = logging.getLogger('pq')

        logger.debug('Starting background processing...')

        if not settings.DEBUG:
            logger.setLevel(logging.WARNING)

        queue.work()
