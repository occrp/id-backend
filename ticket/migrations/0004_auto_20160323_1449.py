# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ticket', '0003_auto_20150911_0932'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ticket',
            name='status',
            field=models.CharField(default=b'new', max_length=70, db_index=True, choices=[(b'new', 'New'), (b'in-progress', 'In Progress'), (b'closed', 'Closed'), (b'cancelled', 'Cancelled')]),
            preserve_default=True,
        ),
    ]
