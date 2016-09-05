# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0005_fake_initial'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='accountrequest',
            unique_together=None,
        ),
        migrations.RemoveField(
            model_name='accountrequest',
            name='user',
        ),
        migrations.DeleteModel(
            name='AccountRequest',
        ),
        migrations.RemoveField(
            model_name='profile',
            name='is_user',
        ),
        migrations.RemoveField(
            model_name='profile',
            name='is_volunteer',
        ),
    ]
