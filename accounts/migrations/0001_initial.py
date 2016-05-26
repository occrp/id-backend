# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import core.mixins


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),

        # If you find your self here because you removed
        # the id-app, please just remove this dependency.
        # It was put in place here only to make sure that
        # the DB-table really existed before running this
        # particular migration.
        ('id', '0018_rename_accountrequests')
    ]

    operations = [
        migrations.CreateModel(
            name='AccountRequest',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('request_type', models.CharField(max_length=64, choices=[(b'requester', 'Information Requester'), (b'volunteer', 'Volunteer')])),
                ('approved', models.NullBooleanField(default=None, verbose_name='Approved')),
                ('date_created', models.DateTimeField(auto_now_add=True, verbose_name='Date Created')),
                ('already_updated', models.BooleanField(default=False)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['request_type', 'approved', 'date_created'],
            },
            bases=(models.Model, core.mixins.DisplayMixin),
        ),
   ]
