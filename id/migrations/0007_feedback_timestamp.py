# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('id', '0006_feedback'),
    ]

    operations = [
        migrations.AddField(
            model_name='feedback',
            name='timestamp',
            field=models.DateTimeField(default=datetime.datetime(2015, 9, 2, 13, 42, 37, 860290, tzinfo=utc), auto_now_add=True),
            preserve_default=False,
        ),
    ]
