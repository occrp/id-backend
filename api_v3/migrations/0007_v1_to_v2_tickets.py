# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2017-08-08 18:36
from __future__ import unicode_literals

from django.db import migrations, models
from django.contrib.contenttypes.models import ContentType

from api_v3.models import Profile, Comment, Ticket, Responder, Attachment


class Migration(migrations.Migration):
    CONTENT_TYPES = {
        'profile_ct_id': ContentType.objects.get_for_model(Profile).id,
        'comment_ct_id': ContentType.objects.get_for_model(Comment).id,
        'ticket_ct_id': ContentType.objects.get_for_model(Ticket).id,
        'responder_ct_id': ContentType.objects.get_for_model(Responder).id,
        'attachment_ct_id': ContentType.objects.get_for_model(Attachment).id
    }

    SQL = """
    --- Migrating v1 tickets.

    insert into api_v3_ticket (
        id,
        status,
        request_type,
        created_at,
        updated_at,
        deadline_at,
        sensitive,
        whysensitive,
        requester_id,
        background,
        connections,
        company_name,
        country,
        first_name,
        last_name,
        born_at,
        business_activities,
        initial_information,
        kind
    )
    select
        ticket_ticket.id,
        ticket_ticket.status,
        ticket_ticket.requester_type as request_type,
        ticket_ticket.created as created_at,
        ticket_ticket.status_updated as updated_at,
        ticket_ticket.deadline as deadline_at,
        ticket_ticket.sensitive,
        ticket_ticket.whysensitive,
        ticket_ticket.requester_id,

        coalesce(
            ticket_otherticket.question,
            ticket_companyticket.background,
            ticket_personticket.background
        ) as background,

        coalesce(
            ticket_companyticket.connections,
            ticket_personticket.aliases,
            ticket_personticket.family
        ) as connections,

        ticket_companyticket.name as company_name,
        ticket_companyticket.country,

        ticket_personticket.name as first_name,
        ticket_personticket.surname as last_name,
        ticket_personticket.dob as born_at,
        ticket_personticket.business_activities,
        ticket_personticket.initial_information,

        case
            when
                (ticket_otherticket.ticket_ptr_id is not null)
                    then 'other'
            when
                (ticket_companyticket.ticket_ptr_id is not null)
                    then 'company_ownership'
            when
                (ticket_personticket.ticket_ptr_id is not null)
                    then 'person_ownership'
        end as kind

        from
            ticket_ticket

        full outer join
            ticket_companyticket on (
                ticket_ticket.id = ticket_companyticket.ticket_ptr_id)
        full outer join
            ticket_personticket on (
                ticket_ticket.id = ticket_personticket.ticket_ptr_id)
        full outer join
            ticket_otherticket on (
                ticket_ticket.id = ticket_otherticket.ticket_ptr_id)
        ;

    --- Migrating v1 ticket responders.

    insert into api_v3_responder (
        ticket_id,
        user_id,
        created_at
    )
    select
        ticket_id,
        profile_id,
        '2000-01-01'
    from
        ticket_ticket_responders;

    --- Migrating v1 ticket comments.

    insert into api_v3_comment (
        body,
        created_at,
        ticket_id,
        user_id
    )
    select
        comment,
        created,
        ticket_id,
        author_id
    from
        ticket_ticketupdate
    where
        comment != ''
    ;

    --- Migrate updates activities;

    insert into activity_action (
        actor_object_id,
        actor_content_type_id,
        target_object_id,
        target_content_type_id,
        verb,
        is_public,
        timestamp
    )
    select
        author_id,
        {profile_ct_id},
        ticket_id,
        {ticket_ct_id},
        case
            when (update_type='close') then 'ticket:update:status_closed'
            when (update_type='cancel') then 'ticket:update:status_cancelled'
            when (update_type='reopen') then 'ticket:update:reopen'
            when (update_type='open') then 'ticket:create'
            when (update_type='update') then 'ticket:update:status_in-progress'
            else concat('ticket:update:', update_type)
        end,
        't',
        created
    from
        ticket_ticketupdate
    where
        update_type != 'entities_attached'
        and comment = '';

    --- Generating comment activities;

    insert into activity_action (
        actor_object_id,
        actor_content_type_id,
        target_object_id,
        target_content_type_id,
        action_object_id,
        action_content_type_id,
        verb,
        is_public,
        timestamp
    )
    select
        user_id,
        {profile_ct_id},
        ticket_id,
        {ticket_ct_id},
        id,
        {comment_ct_id},
        'comment:create',
        't',
        created_at
    from
        api_v3_comment;

    --- Migrating v1 attachments

    insert into api_v3_attachment (
        ticket_id,
        user_id,
        upload,
        created_at
    )
    select
        ticket_id,
        user_id,
        filename,
        created
    from
        ticket_ticketattachment;

    --- Generating attachment activities;

    insert into activity_action (
        actor_object_id,
        actor_content_type_id,
        target_object_id,
        target_content_type_id,
        action_object_id,
        action_content_type_id,
        verb,
        is_public,
        timestamp
    )
    select
        user_id,
        {profile_ct_id},
        ticket_id,
        {ticket_ct_id},
        id,
        {attachment_ct_id},
        'attachment:create',
        't',
        created_at
    from
        api_v3_attachment;

    --- Update the ticket sequence
    select
        setval(
            'api_v3_ticket_id_seq',
            (select max(id)+1 from api_v3_ticket),
            false
        );

    """.format(**CONTENT_TYPES)

    dependencies = [
        ('api_v3', '0006_add_created_at_to_new_responder'),
    ]

    operations = [
        migrations.AlterField(
            model_name='attachment',
            name='upload',
            field=models.CharField(max_length=255)
        ),
        migrations.AlterField(
            model_name='ticket',
            name='whysensitive',
            field=models.CharField(max_length=150, null=True, blank=True)
        ),
        migrations.AlterField(
            model_name='ticket',
            name='first_name',
            field=models.CharField(max_length=512, null=True, blank=True)
        ),
        migrations.AlterField(
            model_name='ticket',
            name='last_name',
            field=models.CharField(max_length=512, null=True, blank=True)
        ),
        migrations.AlterField(
            model_name='ticket',
            name='connections',
            field=models.TextField(max_length=1000, null=True, blank=True)
        ),
        migrations.AlterField(
            model_name='ticket',
            name='sources',
            field=models.TextField(max_length=1000, null=True, blank=True)
        ),
        migrations.AlterField(
            model_name='ticket',
            name='business_activities',
            field=models.TextField(max_length=1000, null=True, blank=True)
        ),
        migrations.AlterField(
            model_name='ticket',
            name='initial_information',
            field=models.TextField(max_length=1000, null=True, blank=True)
        ),
        migrations.AlterField(
            model_name='ticket',
            name='company_name',
            field=models.CharField(max_length=512, null=True, blank=True)
        ),
        migrations.AlterField(
            model_name='ticket',
            name='country',
            field=models.CharField(max_length=100, null=True, blank=True)
        ),
        migrations.RunSQL(SQL)
    ]
