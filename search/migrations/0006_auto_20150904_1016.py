# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('search', '0005_auto_20150902_1641'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='searchresult',
            name='request',
        ),
        migrations.DeleteModel(
            name='SearchResult',
        ),
        migrations.RemoveField(
            model_name='searchrunner',
            name='request',
        ),
        migrations.DeleteModel(
            name='SearchRunner',
        ),
        migrations.AddField(
            model_name='searchrequest',
            name='provider',
            field=models.CharField(default=b'unknown', max_length=250),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='searchrequest',
            name='total_results',
            field=models.IntegerField(default=0),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='searchrequest',
            name='query',
            field=jsonfield.fields.JSONField(),
            preserve_default=True,
        ),
    ]
