# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('id', '0008_auto_20150903_0919'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notification',
            name='action',
            field=models.IntegerField(default=0, choices=[(0, 'None'), (1, 'Add'), (2, 'Edit'), (3, 'Delete'), (4, 'Update'), (5, 'Share'), (1000000, 'Other')]),
            preserve_default=True,
        ),
    ]
