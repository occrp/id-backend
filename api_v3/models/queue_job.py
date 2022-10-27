from django.db import models

from api_v3.misc.queue import queue


class PatchedJSONField(models.JSONField):
    def from_db_value(self, value, *args, **kwargs):
        if value is None:
            return value

        # PATCH: Native JSON field could return a dict already...
        if isinstance(value, dict):
            return value

        # Deal with the rest...
        return super(PatchedJSONField, self).from_db_value(
            value, *args, **kwargs
        )


class QueueJob(models.Model):
    """Queue job model."""

    enqueued_at = models.DateTimeField()
    dequeued_at = models.DateTimeField()
    expected_at = models.DateTimeField()
    schedule_at = models.DateTimeField()
    q_name = models.TextField(blank=False)
    data = PatchedJSONField()

    class Meta:
        managed = False
        db_table = str(queue.table)
