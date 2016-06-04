# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        # If you find your self here because you removed
        # the id-app, please just remove this dependency.
        # It was put in place here only to make sure that
        # the table really existed before running this
        # particular migration.
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
