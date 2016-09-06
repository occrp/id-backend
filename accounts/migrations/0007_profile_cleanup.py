# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0006_remove_requests'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='profile',
            name='address',
        ),
        migrations.RemoveField(
            model_name='profile',
            name='admin_notes',
        ),
        migrations.RemoveField(
            model_name='profile',
            name='availability',
        ),
        migrations.RemoveField(
            model_name='profile',
            name='circulation',
        ),
        migrations.RemoveField(
            model_name='profile',
            name='city',
        ),
        migrations.RemoveField(
            model_name='profile',
            name='conflicts',
        ),
        migrations.RemoveField(
            model_name='profile',
            name='databases',
        ),
        migrations.RemoveField(
            model_name='profile',
            name='expertise',
        ),
        migrations.RemoveField(
            model_name='profile',
            name='findings_visible',
        ),
        migrations.RemoveField(
            model_name='profile',
            name='industry',
        ),
        migrations.RemoveField(
            model_name='profile',
            name='industry_other',
        ),
        migrations.RemoveField(
            model_name='profile',
            name='interests',
        ),
        migrations.RemoveField(
            model_name='profile',
            name='languages',
        ),
        migrations.RemoveField(
            model_name='profile',
            name='last_seen',
        ),
        migrations.RemoveField(
            model_name='profile',
            name='media',
        ),
        migrations.RemoveField(
            model_name='profile',
            name='notes',
        ),
        migrations.RemoveField(
            model_name='profile',
            name='organization_membership',
        ),
        migrations.RemoveField(
            model_name='profile',
            name='postal_code',
        ),
        migrations.RemoveField(
            model_name='profile',
            name='province',
        ),
        migrations.RemoveField(
            model_name='profile',
            name='title',
        ),
        migrations.AddField(
            model_name='profile',
            name='organization',
            field=models.CharField(max_length=1024, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='profile',
            name='phone_number',
            field=models.CharField(max_length=255, blank=True),
            preserve_default=True,
        ),
    ]
