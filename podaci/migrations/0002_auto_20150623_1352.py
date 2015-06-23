# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('podaci', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='podacifile',
            name='created_by',
            field=models.ForeignKey(related_name='created_files', blank=True, to=settings.AUTH_USER_MODEL, null=True),
            preserve_default=True,
        ),
    ]
