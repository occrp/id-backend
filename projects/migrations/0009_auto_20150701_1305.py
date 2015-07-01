# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0008_auto_20150629_1436'),
    ]

    operations = [
        migrations.AlterField(
            model_name='story',
            name='published',
            field=models.DateTimeField(null=True),
            preserve_default=True,
        ),
    ]
