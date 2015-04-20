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
            name='SearchRequest',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('search_type', models.CharField(max_length=30, choices=[(b'image', b'Image search'), (b'podaci', b'Document search'), (b'osoba', b'Graph search')])),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('query', models.TextField()),
                ('requester', models.ForeignKey(to=settings.AUTH_USER_MODEL, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SearchResult',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('provider', models.CharField(max_length=30)),
                ('found', models.DateTimeField(auto_now_add=True)),
                ('data', models.TextField()),
                ('request', models.ForeignKey(to='search.SearchRequest')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SearchRunner',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=30)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('results', models.IntegerField(default=0)),
                ('done', models.BooleanField(default=False)),
                ('request', models.ForeignKey(to='search.SearchRequest')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
