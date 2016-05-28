# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations, connection
from django.db.utils import OperationalError, ProgrammingError
import django.utils.timezone
from django.conf import settings
import core.mixins


def got_old_migrations():
    """
    Check if we got old migrations - i.e.,
    we are running on a system that has
    migrations applied before they were purged
    (which happened in May/June 2016).
    """

    cursor = connection.cursor()

    try:
        cursor.execute("SELECT id FROM django_migrations WHERE app='accounts' AND name='0003_network'")

        if (len(cursor.fetchall()) > 0):
            return True

        return False

    # No such table, we can return False
    except OperationalError:
        return False

    except ProgrammingError:
        return False

class Migration(migrations.Migration):
    def __init__(self, name, app_label):
        """
        Detect if we got old migrations - see got_old_migrations().
        If so, put in place operations that will rename tables.
        """

        super(Migration, self).__init__(name, app_label)

        if (got_old_migrations() == True):
            self.operations = self.perhaps_run_operations

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    perhaps_run_operations = [
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

    # By default, we don't do anything,
    # but, see __init__() for situations
    # were we do something
    operations = []
