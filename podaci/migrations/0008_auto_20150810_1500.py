# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('podaci', '0007_podacicollection_shared'),
    ]

    operations = [
        migrations.AddField(
            model_name='podacicollection',
            name='shared_with',
            field=models.ManyToManyField(to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='podacicollection',
            unique_together=set([('name', 'owner')]),
        ),
        migrations.RemoveField(
            model_name='podacicollection',
            name='shared',
        ),
    ]
