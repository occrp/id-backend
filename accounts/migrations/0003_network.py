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
        ('id', '0021_rename_network'),

        ('accounts', '0002_initial'),
    ]

    state_operations = [
        migrations.CreateModel(
            name='Network',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('short_name', models.CharField(max_length=50)),
                ('long_name', models.CharField(max_length=100, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(state_operations=state_operations)
    ]



