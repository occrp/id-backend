# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('podaci', '0006_auto_20150807_1515'),
    ]

    operations = [
        migrations.AddField(
            model_name='podacicollection',
            name='shared',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
