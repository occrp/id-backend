# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('projects', '0002_auto_20150710_1127'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='coordinators',
            field=models.ManyToManyField(related_name='coordinators', to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='project',
            name='users',
            field=models.ManyToManyField(related_name='members', to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
    ]
