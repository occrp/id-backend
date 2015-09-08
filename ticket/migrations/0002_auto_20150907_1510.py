# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('podaci', '0015_auto_20150904_1622'),
        ('ticket', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='ticket',
            name='tag',
        ),
        migrations.AddField(
            model_name='ticket',
            name='files',
            field=models.ManyToManyField(related_name='tickets', to='podaci.PodaciFile'),
            preserve_default=True,
        ),
    ]
