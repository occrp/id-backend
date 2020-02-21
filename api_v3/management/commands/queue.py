from django.core.management.base import BaseCommand
from api_v3.misc.queue import queue


class Command(BaseCommand):
    help = 'Starts the jobs queue'

    def handle(self, *args, **options):
        """Runs the queue."""
        queue.work()
