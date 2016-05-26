# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('id', '0015_delete_databasescraperequest'),
    ]

    operations = [
        migrations.RunSQL(
            "ALTER TABLE id_feedback RENAME TO feedback_feedback"
        ),
    ]
