# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('id', '0004_auto_20150805_0958'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='profile',
            name='abbr',
        ),
    ]
