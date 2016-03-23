# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('id', '0013_auto_20160202_1714'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='is_staff',
            field=models.BooleanField(default=False, db_index=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='profile',
            name='is_user',
            field=models.BooleanField(default=True, db_index=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='profile',
            name='is_volunteer',
            field=models.BooleanField(default=False, db_index=True),
            preserve_default=True,
        ),
    ]
