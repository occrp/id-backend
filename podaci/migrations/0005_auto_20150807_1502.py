# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import podaci.models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('podaci', '0004_auto_20150625_1322'),
    ]

    operations = [
        migrations.CreateModel(
            name='PodaciCollection',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=300)),
                ('description', models.TextField(blank=True)),
                ('files', models.ManyToManyField(related_name='collections', to='podaci.PodaciFile')),
                ('owner', models.ForeignKey(related_name='created_collections', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
            },
            bases=(models.Model, ),
        ),
        migrations.RemoveField(
            model_name='podacitagchangelog',
            name='ref',
        ),
        migrations.RemoveField(
            model_name='podacitagchangelog',
            name='user',
        ),
        migrations.DeleteModel(
            name='PodaciTagChangelog',
        ),
        migrations.RemoveField(
            model_name='podacitag',
            name='allowed_users_read',
        ),
        migrations.RemoveField(
            model_name='podacitag',
            name='allowed_users_write',
        ),
        migrations.RemoveField(
            model_name='podacitag',
            name='date_added',
        ),
        migrations.RemoveField(
            model_name='podacitag',
            name='parents',
        ),
        migrations.RemoveField(
            model_name='podacitag',
            name='public_read',
        ),
        migrations.RemoveField(
            model_name='podacitag',
            name='staff_read',
        ),
        migrations.AlterField(
            model_name='podacitag',
            name='name',
            field=models.CharField(unique=True, max_length=100),
            preserve_default=True,
        ),
    ]
