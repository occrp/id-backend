# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('id', '0007_feedback_timestamp'),
    ]

    operations = [
        migrations.AddField(
            model_name='notification',
            name='action',
            field=models.IntegerField(default=0, choices=[(0, 'None'), (1, 'Add'), (2, 'Edit'), (3, 'Delete'), (4, 'Update'), (5, 'Share'), (100, 'Other')]),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='notification',
            name='stream',
            field=models.CharField(default=b'id:wail', max_length=200),
            preserve_default=True,
        ),
    ]
