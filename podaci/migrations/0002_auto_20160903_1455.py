# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ticket', '0004_auto_20160903_1455'),
        ('podaci', '0001_initial'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='podacicollection',
            unique_together=None,
        ),
        migrations.RemoveField(
            model_name='podacicollection',
            name='files',
        ),
        migrations.RemoveField(
            model_name='podacicollection',
            name='owner',
        ),
        migrations.RemoveField(
            model_name='podacicollection',
            name='shared_with',
        ),
        migrations.DeleteModel(
            name='PodaciCollection',
        ),
        migrations.RemoveField(
            model_name='podacifile',
            name='allowed_users_read',
        ),
        migrations.RemoveField(
            model_name='podacifile',
            name='allowed_users_write',
        ),
        migrations.RemoveField(
            model_name='podacifile',
            name='created_by',
        ),
        migrations.RemoveField(
            model_name='podacifile',
            name='tags',
        ),
        migrations.DeleteModel(
            name='PodaciFile',
        ),
        migrations.DeleteModel(
            name='PodaciTag',
        ),
    ]
