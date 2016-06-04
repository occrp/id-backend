# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import core.mixins


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('accounts', '0001_initial')
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='accountrequest',
            unique_together=None,
        ),
        migrations.AlterUniqueTogether(
            name='accountrequest',
            unique_together=set([('user', 'request_type')]),
        ),


   ]
