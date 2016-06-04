# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db


class Migration(migrations.Migration):

    dependencies = [
        ('id', '0015_delete_databasescraperequest'),
    ]

    operations = [
        migrations.RunSQL(
            "ALTER TABLE id_feedback RENAME TO feedback_feedback"
        ),
        # If running on PostgreSQL, rename the sequencer also - no sequencer left behind!
        migrations.RunSQL(
            "ALTER SEQUENCE id_feedback_id_seq RENAME TO feedback_feedback_id_seq" if django.db.connection.vendor == "postgresql" \
             else "SELECT 1"
        ),

    ]
