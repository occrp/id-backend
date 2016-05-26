# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('id', '0016_rename_feedback')
    ]

    operations = [
        migrations.CreateModel(
            name='Feedback',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100)),
                ('email', models.EmailField(max_length=75)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('message', models.TextField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
