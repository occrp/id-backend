# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('projects', '0003_story_title'),
    ]

    operations = [
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
    ]
