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
            name='Project',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=250)),
                ('coordinator', models.ForeignKey(related_name='coordinator', to=settings.AUTH_USER_MODEL)),
                ('users', models.ManyToManyField(related_name='members', to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Story',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=250)),
                ('published', models.DateField()),
                ('podaci_root', models.CharField(max_length=50)),
                ('artists', models.ManyToManyField(related_name='artists', to=settings.AUTH_USER_MODEL)),
                ('copy_editors', models.ManyToManyField(related_name='copy_editors', to=settings.AUTH_USER_MODEL)),
                ('editors', models.ManyToManyField(related_name='editors', to=settings.AUTH_USER_MODEL)),
                ('fact_checkers', models.ManyToManyField(related_name='fact_checkers', to=settings.AUTH_USER_MODEL)),
                ('project', models.ForeignKey(to='projects.Project')),
                ('reporters', models.ManyToManyField(related_name='reporters', to=settings.AUTH_USER_MODEL)),
                ('researchers', models.ManyToManyField(related_name='researchers', to=settings.AUTH_USER_MODEL)),
                ('translators', models.ManyToManyField(related_name='translators', to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='StoryStatus',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('timestamp', models.DateTimeField(auto_now=True)),
                ('deadline', models.DateTimeField()),
                ('status', models.IntegerField(choices=[(1, b'Research'), (2, b'Writing'), (3, b'Editing'), (4, b'Copy-editing'), (5, b'Fact-checking'), (6, b'Translation'), (7, b'Artwork'), (8, b'Postponed'), (10, b'Embargoed'), (11, b'Published')])),
                ('description', models.CharField(max_length=500)),
                ('set_by', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
                ('story', models.ForeignKey(to='projects.Story')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='StoryTranslation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('language_code', models.CharField(max_length=2)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('verified', models.BooleanField(default=False)),
                ('live', models.BooleanField(default=False)),
                ('title', models.CharField(max_length=250)),
                ('text', models.TextField()),
                ('translator', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='StoryVersion',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('title', models.CharField(max_length=250)),
                ('text', models.TextField()),
                ('authored', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
                ('story', models.ForeignKey(related_name='versions', to='projects.Story')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='storytranslation',
            name='version',
            field=models.ForeignKey(to='projects.StoryVersion'),
            preserve_default=True,
        ),
    ]
