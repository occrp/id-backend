# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('id', '0021_rename_network'),
        ('accounts', '0003_network'),
    ]

    operations = [
        # Add foreignkey to Network back to Profile
        # This completes our cycle.
        migrations.AlterField(
            model_name='profile',
            name='network',
            field=models.ForeignKey(related_name='members', blank=True, to='accounts.Network', null=True),
            preserve_default=True,
        ),
    ]
