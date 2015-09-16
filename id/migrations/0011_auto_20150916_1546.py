# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('id', '0010_auto_20150907_1249'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='industry_other',
            field=models.CharField(max_length=256, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='profile',
            name='title',
            field=models.CharField(max_length=256, blank=True),
            preserve_default=True,
        ),
    ]
