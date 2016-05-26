# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('id', '0017_delete_feedback'),
    ]

    operations = [
        # Remove unique together constraint
        # - migrations will want this because
        # we are moving the 'AccountRequest' model
        migrations.AlterUniqueTogether(
            name='accountrequest',
            unique_together=None,
        ),

        # Then simply rename id_accountrequest so that
        # the models-system thinks it is part of the
        # accounts app
        migrations.RunSQL(
            "ALTER TABLE id_accountrequest RENAME TO accounts_accountrequest"
        ),

        # At this point, we have already renamed 'id_accountrequest' 
        # to 'accounts_accountrequest', and so there is no 
        # 'id_accountrequest'. Now create 'id_accountrequest'
        # by hand, and keep it empty. Remember, the data is already safe.
        migrations.RunSQL(
            'CREATE TABLE "id_accountrequest" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "request_type" varchar(64) NOT NULL, "approved" bool NULL, "date_created" datetime NOT NULL, "already_updated" bool NOT NULL, "user_id" integer NOT NULL REFERENCES "id_profile" ("id"))'
        ),

        # Remove the user-field from AccountRequest (foreign-key)
        migrations.RemoveField(
            model_name='accountrequest',
            name='user',
        ),

        # And then just remove the model, like that. It is already empty.
        migrations.DeleteModel(
            name='AccountRequest',
        ),
    ]
