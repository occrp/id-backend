# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('search', '0003_auto_20150520_1047'),
    ]

    operations = [
        migrations.AlterField(
            model_name='searchrequest',
            name='search_type',
            field=models.CharField(max_length=30, choices=[(b'document', b'Document search'), (b'image', b'Image search')]),
            preserve_default=True,
        ),
    ]
