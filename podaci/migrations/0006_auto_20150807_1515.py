# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('podaci', '0005_auto_20150807_1502'),
    ]

    operations = [
        migrations.RenameField(
            model_name='podacifilenote',
            old_name='description',
            new_name='text',
        ),
    ]
