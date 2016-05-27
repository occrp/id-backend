# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('id', '0019_auto_20160527_1115'),
    ]

    operations = [
        # Begin by removing the ForeignKey element
        # from id.models.Profile - this will enable
        # us to work with the Network model.
        #
        # We will add the ForeignKey later on, in
        # migration id/migrations/0022_add_profile_foreignkey_to_network.py

        migrations.AlterField(
            model_name='profile',
            name='network',
            field=models.IntegerField(null=True, blank=True),
            preserve_default=True,
        ),
    ]
