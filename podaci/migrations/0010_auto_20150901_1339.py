# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('podaci', '0009_auto_20150827_1334'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='podacifile',
            name='name',
        ),
        migrations.AlterField(
            model_name='podacifile',
            name='filename',
            field=models.CharField(max_length=256),
            preserve_default=True,
        ),
    ]
