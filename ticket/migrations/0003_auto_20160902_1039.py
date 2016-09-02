# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


def copy_podaci_files(apps, schema_editor):
    Ticket = apps.get_model("ticket", "Ticket")
    TicketAttachment = apps.get_model("ticket", "TicketAttachment")
    for ticket in Ticket.objects.all():
        for pfile in ticket.files.all():
            attach = TicketAttachment()
            attach.ticket = ticket
            user = pfile.created_by
            for writer in pfile.allowed_users_write.all():
                if writer != ticket.requester and user is None:
                    user = writer
            attach.user = user
            attach.size = pfile.size
            attach.sha256 = pfile.sha256
            attach.mimetype = pfile.mimetype
            attach.filename = pfile.filename
            attach.created = pfile.date_added
            attach.save()


class Migration(migrations.Migration):

    dependencies = [
        ('ticket', '0002_ticketattachment'),
    ]

    operations = [
        migrations.RunPython(copy_podaci_files),
    ]
