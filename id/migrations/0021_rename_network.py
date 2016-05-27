# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('id', '0020_remove_profile_foreignkey_to_network'),
    ]

    database_operations = [
        # First, rename 'id_network' to 'accounts_network'
        migrations.AlterModelTable('Network', 'accounts_network')
    ]

    state_operations = [
        # Remove 'Network' from the app's history
        migrations.DeleteModel('Network')
    ]

    operations = [
        # Actually perform things.
        migrations.SeparateDatabaseAndState(
            database_operations=database_operations,
            state_operations=state_operations
        )
    ]
