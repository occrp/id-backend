# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
import core.mixins
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('ticket', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='TicketAttachment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('filename', models.CharField(max_length=256)),
                ('title', models.CharField(max_length=300, null=True, blank=True)),
                ('sha256', models.CharField(max_length=65)),
                ('size', models.IntegerField(default=0)),
                ('mimetype', models.CharField(max_length=65)),
                ('created', models.DateTimeField(default=datetime.datetime.now)),
                ('ticket', models.ForeignKey(to='ticket.Ticket')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model, core.mixins.NotificationMixin, core.mixins.DisplayMixin),
        ),
    ]
