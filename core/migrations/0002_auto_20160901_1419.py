# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='auditlog',
            name='user',
        ),
        migrations.DeleteModel(
            name='AuditLog',
        ),
        migrations.AlterField(
            model_name='notification',
            name='action',
            field=models.CharField(max_length=255, null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='notification',
            name='model',
            field=models.CharField(max_length=255, null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='notification',
            name='module',
            field=models.CharField(max_length=255, null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='notification',
            name='project',
            field=models.CharField(max_length=255, null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='notification',
            name='text',
            field=models.CharField(max_length=10000),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='notification',
            name='url_params',
            field=models.CharField(max_length=2000, null=True, blank=True),
            preserve_default=True,
        ),
    ]
