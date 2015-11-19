# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_notification_url'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notification',
            name='text',
            field=models.CharField(max_length=200),
            preserve_default=True,
        ),
    ]
