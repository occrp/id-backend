# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ticket', '0003_auto_20160902_1039'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='ticketattachment',
            name='title',
        ),
        migrations.AlterField(
            model_name='ticketattachment',
            name='ticket',
            field=models.ForeignKey(related_name='attachments', to='ticket.Ticket'),
            preserve_default=True,
        ),
    ]
