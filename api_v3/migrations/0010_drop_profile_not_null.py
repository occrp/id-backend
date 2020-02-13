# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2018-06-15 6:12


from django.db import migrations, connection


class Migration(migrations.Migration):

    dependencies = [
        ('api_v3', '0009_added_subscriber'),
    ]

    COLUMNS_SQL = """
        SELECT column_name FROM information_schema.columns
        WHERE table_name = 'accounts_profile' AND
        column_name IN
        ('user_created', 'requester_type', 'organization', 'last_login')
        AND is_nullable = 'NO';
        """

    DROP_NOT_NULL_SQL = """
        ALTER TABLE accounts_profile ALTER COLUMN {} DROP NOT NULL;
        """

    operations = []

    with connection.cursor() as cursor:
        cursor.execute(COLUMNS_SQL)
        cols = cursor.fetchall()

        for c in cols:
            operations.append(migrations.RunSQL(DROP_NOT_NULL_SQL.format(c[0])))
