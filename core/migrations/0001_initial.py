# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='AuditLog',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('level', models.IntegerField()),
                ('module', models.CharField(max_length=100)),
                ('filename', models.CharField(max_length=100)),
                ('lineno', models.IntegerField()),
                ('funcname', models.CharField(max_length=100)),
                ('message', models.TextField(null=True, blank=True)),
                ('excinfo', models.TextField(null=True, blank=True)),
                ('exctext', models.TextField(null=True, blank=True)),
                ('process', models.IntegerField()),
                ('thread', models.IntegerField()),
                ('ip', models.IPAddressField(null=True, blank=True)),
                ('timestamp', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('is_seen', models.BooleanField(default=False)),
                ('text', models.CharField(max_length=200)),
                ('url_base', models.CharField(max_length=50, null=True, blank=True)),
                ('url_params', models.CharField(max_length=200, null=True, blank=True)),
                ('url', models.URLField(null=True, blank=True)),
                ('project', models.CharField(max_length=10, null=True)),
                ('module', models.CharField(max_length=20, null=True)),
                ('model', models.CharField(max_length=30, null=True)),
                ('instance', models.IntegerField(null=True)),
                ('action', models.CharField(max_length=20, null=True)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-timestamp'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='NotificationSubscription',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('project', models.CharField(max_length=10, null=True)),
                ('module', models.CharField(max_length=20, null=True)),
                ('model', models.CharField(max_length=30, null=True)),
                ('instance', models.IntegerField(null=True)),
                ('action', models.CharField(max_length=20, null=True)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='notificationsubscription',
            unique_together=set([('user', 'project', 'module', 'model', 'instance', 'action')]),
        ),
    ]
