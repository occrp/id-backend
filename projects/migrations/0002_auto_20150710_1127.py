# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='projectuser',
            name='project',
        ),
        migrations.RemoveField(
            model_name='projectuser',
            name='user',
        ),
        migrations.RemoveField(
            model_name='project',
            name='users',
        ),
        migrations.DeleteModel(
            name='ProjectUser',
        ),
    ]
