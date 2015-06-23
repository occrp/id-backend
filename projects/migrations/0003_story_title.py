# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0002_story_storystatus'),
    ]

    operations = [
        migrations.AddField(
            model_name='story',
            name='title',
            field=models.CharField(default='empty', max_length=250),
            preserve_default=False,
        ),
    ]
