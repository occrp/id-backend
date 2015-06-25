# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('podaci', '0003_auto_20150623_1403'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='podacifile',
            name='changelog',
        ),
        migrations.RemoveField(
            model_name='podacifile',
            name='notes',
        ),
        migrations.AlterField(
            model_name='podacifilechangelog',
            name='ref',
            field=models.ForeignKey(related_name='logs', to='podaci.PodaciFile'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='podacifilenote',
            name='ref',
            field=models.ForeignKey(related_name='notes', to='podaci.PodaciFile'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='podacifiletriples',
            name='ref',
            field=models.ForeignKey(related_name='metadata', to='podaci.PodaciFile'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='podacitagchangelog',
            name='ref',
            field=models.ForeignKey(related_name='logs', to='podaci.PodaciTag'),
            preserve_default=True,
        ),
    ]
