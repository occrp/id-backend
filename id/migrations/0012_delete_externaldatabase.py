# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('id', '0011_auto_20150916_1546'),
    ]

    database_operations = [
        migrations.AlterModelTable('ExternalDatabase', 'databases_externaldatabase')
    ]

    state_operations = [
        migrations.DeleteModel('ExternalDatabase')
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=database_operations,
            state_operations=state_operations)
    ]
