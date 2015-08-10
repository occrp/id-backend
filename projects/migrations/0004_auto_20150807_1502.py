# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0003_auto_20150710_1140'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='projectplan',
            options={'ordering': ['order']},
        ),
        migrations.AlterModelOptions(
            name='story',
            options={'ordering': ['-id']},
        ),
        migrations.AlterModelOptions(
            name='storystatus',
            options={'ordering': ['-timestamp']},
        ),
        migrations.AlterModelOptions(
            name='storytranslation',
            options={'ordering': ['-timestamp']},
        ),
        migrations.AlterModelOptions(
            name='storyversion',
            options={'ordering': ['-timestamp']},
        ),
    ]
