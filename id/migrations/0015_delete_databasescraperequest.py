# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('id', '0014_auto_20160323_1448'),
    ]

    operations = [
        migrations.DeleteModel(
            name='DatabaseScrapeRequest',
        ),
    ]
