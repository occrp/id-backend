# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('podaci', '0013_auto_20150902_1456'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='podacitag',
            name='icon',
        ),
    ]
