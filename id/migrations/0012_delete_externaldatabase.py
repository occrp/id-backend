# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations
import django.db

class Migration(migrations.Migration):
    dependencies = [
        ('id', '0011_auto_20150916_1546'),
    ]

    database_operations = [
        migrations.AlterModelTable('ExternalDatabase', 'databases_externaldatabase'),

        # If running on PostgreSQL, rename the sequencer also - no sequencer left behind!
        migrations.RunSQL(
            "ALTER SEQUENCE id_externaldatabase_id_seq RENAME TO databases_externaldatabase_id_seq" if django.db.connection.vendor == "postgresql" \
             else "SELECT 1"
        )
    ]

    state_operations = [
        migrations.DeleteModel('ExternalDatabase')
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=database_operations,
            state_operations=state_operations)
    ]
