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
            name='PodaciFile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200)),
                ('date_added', models.DateTimeField(auto_now_add=True)),
                ('public_read', models.BooleanField(default=False)),
                ('staff_read', models.BooleanField(default=False)),
                ('schema_version', models.IntegerField(default=3)),
                ('title', models.CharField(max_length=300)),
                ('is_resident', models.BooleanField(default=True)),
                ('filename', models.CharField(max_length=256, blank=True)),
                ('url', models.URLField(blank=True)),
                ('sha256', models.CharField(max_length=65)),
                ('size', models.IntegerField(default=0)),
                ('mimetype', models.CharField(max_length=65)),
                ('description', models.TextField(blank=True)),
                ('is_indexed', models.BooleanField(default=False)),
                ('is_entity_extracted', models.BooleanField(default=False)),
                ('allowed_users_read', models.ManyToManyField(related_name='podacifile_files_perm_read', to=settings.AUTH_USER_MODEL)),
                ('allowed_users_write', models.ManyToManyField(related_name='podacifile_files_perm_write', to=settings.AUTH_USER_MODEL)),
                ('created_by', models.ForeignKey(related_name='created_files', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='PodaciFileChangelog',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('description', models.CharField(max_length=200)),
                ('ref', models.ForeignKey(to='podaci.PodaciFile')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='PodaciFileNote',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('description', models.TextField()),
                ('ref', models.ForeignKey(to='podaci.PodaciFile')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='PodaciFileTriples',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('key', models.CharField(max_length=200)),
                ('value', models.TextField()),
                ('ref', models.ForeignKey(to='podaci.PodaciFile')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='PodaciTag',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200)),
                ('date_added', models.DateTimeField(auto_now_add=True)),
                ('public_read', models.BooleanField(default=False)),
                ('staff_read', models.BooleanField(default=False)),
                ('icon', models.CharField(max_length=100)),
                ('allowed_users_read', models.ManyToManyField(related_name='podacitag_files_perm_read', to=settings.AUTH_USER_MODEL)),
                ('allowed_users_write', models.ManyToManyField(related_name='podacitag_files_perm_write', to=settings.AUTH_USER_MODEL)),
                ('parents', models.ManyToManyField(related_name='children', to='podaci.PodaciTag')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='PodaciTagChangelog',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('description', models.CharField(max_length=200)),
                ('ref', models.ForeignKey(to='podaci.PodaciTag')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='podacifile',
            name='tags',
            field=models.ManyToManyField(related_name='files', to='podaci.PodaciTag'),
            preserve_default=True,
        ),
    ]
