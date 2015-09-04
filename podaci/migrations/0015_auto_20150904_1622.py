# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('podaci', '0014_remove_podacitag_icon'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='podacifilechangelog',
            name='ref',
        ),
        migrations.RemoveField(
            model_name='podacifilechangelog',
            name='user',
        ),
        migrations.DeleteModel(
            name='PodaciFileChangelog',
        ),
    ]
