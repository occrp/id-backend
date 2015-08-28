# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('podaci', '0008_auto_20150810_1500'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='podacicollection',
            options={'ordering': ('name',)},
        ),
        migrations.AlterField(
            model_name='podacicollection',
            name='owner',
            field=models.ForeignKey(related_name='collections', default=1, to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
    ]
