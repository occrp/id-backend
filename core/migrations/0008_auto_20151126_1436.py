# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_auto_20151126_1433'),
    ]

    operations = [
        migrations.AlterField(
            model_name='auditlog',
            name='timestamp',
            field=models.DateTimeField(auto_now=True),
            preserve_default=True,
        ),
    ]
