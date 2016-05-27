# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
from django.conf import settings
import core.mixins


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.RunSQL(
            "ALTER TABLE id_profile RENAME TO accounts_profile"
        ),

        migrations.RunSQL(
            "ALTER TABLE id_profile_groups RENAME TO accounts_profile_groups"
        ),

        migrations.RunSQL(
            "ALTER TABLE id_profile_user_permissions RENAME TO accounts_profile_user_permissions"
        ),
    ]
