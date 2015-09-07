# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_remove_notification_action'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='notification',
            name='channel',
        ),
        migrations.AddField(
            model_name='notification',
            name='action',
            field=models.CharField(max_length=20, null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='notification',
            name='instance',
            field=models.IntegerField(null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='notification',
            name='model',
            field=models.CharField(max_length=30, null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='notification',
            name='module',
            field=models.CharField(max_length=20, null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='notification',
            name='project',
            field=models.CharField(max_length=10, null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='notificationsubscription',
            name='action',
            field=models.CharField(max_length=20, null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='notificationsubscription',
            name='instance',
            field=models.IntegerField(null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='notificationsubscription',
            name='model',
            field=models.CharField(max_length=30, null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='notificationsubscription',
            name='module',
            field=models.CharField(max_length=20, null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='notificationsubscription',
            name='project',
            field=models.CharField(max_length=10, null=True),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='notificationsubscription',
            unique_together=set([('user', 'project', 'module', 'model', 'instance', 'action')]),
        ),
        migrations.RemoveField(
            model_name='notificationsubscription',
            name='channel',
        ),
    ]
