# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0002_projectplan'),
    ]

    operations = [
        migrations.AlterField(
            model_name='story',
            name='project',
            field=models.ForeignKey(related_name='stories', to='projects.Project'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='story',
            name='published',
            field=models.DateField(null=True),
            preserve_default=True,
        ),
    ]
