from django.db import models
from django.conf import settings
from django.contrib.postgres.fields import JSONField

from api_v3.misc.queue import queue


class QueueJob(models.Model):
    """Queue job model."""

    enqueued_at = models.DateTimeField()
    dequeued_at = models.DateTimeField()
    expected_at = models.DateTimeField()
    schedule_at = models.DateTimeField()
    q_name = models.TextField(blank=False)
    data = JSONField()

    class Meta:
        managed = False
        db_table = str(queue.table)
