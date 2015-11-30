# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('databases', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='externaldatabase',
            name='blog_post',
            field=models.URLField(verbose_name='Blog Post', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='externaldatabase',
            name='notes',
            field=models.TextField(verbose_name='Notes', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='externaldatabase',
            name='video_url',
            field=models.URLField(verbose_name='YouTube Video Url', blank=True),
            preserve_default=True,
        ),
    ]
