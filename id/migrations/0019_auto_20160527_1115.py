# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('id', '0018_rename_accountrequests'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='center',
            name='networks',
        ),
        migrations.DeleteModel(
            name='Center',
        ),
    ]
