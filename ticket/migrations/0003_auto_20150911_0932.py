# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ticket', '0002_auto_20150907_1510'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ticket',
            name='deadline',
            field=models.DateField(help_text='How soon do you need this request fulfilled? We will try to meet your deadline, but please note that our researchers are quite busy -- give them as much time as you possibly can!', null=True, verbose_name='Deadline', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='ticket',
            name='is_public',
            field=models.BooleanField(default=False, help_text='Are you okay with the findings becoming public immediately?', verbose_name='Public?'),
            preserve_default=True,
        ),
    ]
