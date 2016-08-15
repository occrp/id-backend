# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import core.mixins


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='PodaciCollection',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=300)),
                ('description', models.TextField(blank=True)),
            ],
            options={
                'ordering': ('name',),
            },
            bases=(core.mixins.NotificationMixin, models.Model),
        ),
        migrations.CreateModel(
            name='PodaciFile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('filename', models.CharField(max_length=256)),
                ('date_added', models.DateTimeField(auto_now_add=True)),
                ('public_read', models.BooleanField(default=False)),
                ('staff_read', models.BooleanField(default=False)),
                ('schema_version', models.IntegerField(default=3)),
                ('title', models.CharField(max_length=300, null=True, blank=True)),
                ('url', models.URLField(blank=True)),
                ('sha256', models.CharField(max_length=65)),
                ('size', models.IntegerField(default=0)),
                ('mimetype', models.CharField(max_length=65)),
                ('description', models.TextField(blank=True)),
                ('is_entity_extracted', models.BooleanField(default=False)),
                ('allowed_users_read', models.ManyToManyField(related_name='podacifile_files_perm_read', to=settings.AUTH_USER_MODEL)),
                ('allowed_users_write', models.ManyToManyField(related_name='podacifile_files_perm_write', to=settings.AUTH_USER_MODEL)),
                ('created_by', models.ForeignKey(related_name='created_files', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
            },
            bases=(core.mixins.NotificationMixin, models.Model),
        ),
        migrations.CreateModel(
            name='PodaciTag',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=100)),
            ],
            options={
            },
            bases=(core.mixins.NotificationMixin, models.Model),
        ),
        migrations.AddField(
            model_name='podacifile',
            name='tags',
            field=models.ManyToManyField(related_name='files', to='podaci.PodaciTag'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='podacicollection',
            name='files',
            field=models.ManyToManyField(related_name='collections', to='podaci.PodaciFile'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='podacicollection',
            name='owner',
            field=models.ForeignKey(related_name='collections', default=1, to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
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
    ]
