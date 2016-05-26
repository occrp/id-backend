# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('id', '0016_rename_feedback'),
    ]

    operations = [
        migrations.RunSQL(
            "CREATE TABLE id_feedback (texti varchar(100))"
        ),

        migrations.DeleteModel(
            name='Feedback',
        ),
    ]
