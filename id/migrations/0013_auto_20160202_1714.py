# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('id', '0012_delete_externaldatabase'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='is_user',
            field=models.BooleanField(default=True),
            preserve_default=True,
        ),
    ]
