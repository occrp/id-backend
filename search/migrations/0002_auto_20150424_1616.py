# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('search', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='searchrequest',
            name='search_type',
            field=models.CharField(max_length=30, choices=[(b'image', b'Image search'), (b'social', b'Social Network search'), (b'podaci', b'Document search'), (b'osoba', b'Graph search')]),
            preserve_default=True,
        ),
    ]
