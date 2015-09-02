# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('podaci', '0012_auto_20150901_1349'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='podacifilenote',
            name='ref',
        ),
        migrations.RemoveField(
            model_name='podacifilenote',
            name='user',
        ),
        migrations.DeleteModel(
            name='PodaciFileNote',
        ),
        migrations.RemoveField(
            model_name='podacifiletriples',
            name='ref',
        ),
        migrations.DeleteModel(
            name='PodaciFileTriples',
        ),
        migrations.RemoveField(
            model_name='podacifile',
            name='is_indexed',
        ),
        migrations.RemoveField(
            model_name='podacifile',
            name='is_resident',
        ),
    ]
