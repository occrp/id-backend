# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0009_auto_20150701_1305'),
    ]

    operations = [
        migrations.RenameField(
            model_name='storyversion',
            old_name='authored',
            new_name='author',
        ),
    ]
