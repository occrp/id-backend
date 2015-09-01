# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('podaci', '0010_auto_20150901_1339'),
    ]

    operations = [
        migrations.AlterField(
            model_name='podacifile',
            name='title',
            field=models.CharField(max_length=300, blank=True),
            preserve_default=True,
        ),
    ]
