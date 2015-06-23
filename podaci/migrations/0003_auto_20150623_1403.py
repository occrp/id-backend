# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('podaci', '0002_auto_20150623_1352'),
    ]

    operations = [
        migrations.AddField(
            model_name='podacifile',
            name='changelog',
            field=models.ManyToManyField(to='podaci.PodaciFileChangelog'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='podacifile',
            name='notes',
            field=models.ManyToManyField(to='podaci.PodaciFileNote'),
            preserve_default=True,
        ),
    ]
