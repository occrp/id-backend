# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ticket', '0004_auto_20160323_1449'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='ticket',
            name='volunteers',
        ),
    ]
