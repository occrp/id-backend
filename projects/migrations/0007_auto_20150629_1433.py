# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0006_story_description'),
    ]

    operations = [
        migrations.RenameField(
            model_name='story',
            old_name='description',
            new_name='thesis',
        ),
    ]
