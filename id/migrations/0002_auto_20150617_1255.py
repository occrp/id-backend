# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('id', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='accountrequest',
            options={'ordering': ['request_type', 'approved', 'date_created']},
        ),
        migrations.AlterField(
            model_name='accountrequest',
            name='request_type',
            field=models.CharField(max_length=64, choices=[(b'requester', 'Information Requester'), (b'volunteer', 'Volunteer')]),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='accountrequest',
            unique_together=set([('user', 'request_type')]),
        ),
    ]
