# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_auto_20151126_1436'),
    ]

    operations = [
        migrations.AlterField(
            model_name='auditlog',
            name='excinfo',
            field=models.TextField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='auditlog',
            name='exctext',
            field=models.TextField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='auditlog',
            name='message',
            field=models.TextField(null=True, blank=True),
            preserve_default=True,
        ),
    ]
