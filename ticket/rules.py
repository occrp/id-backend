from __future__ import absolute_import

from rules import add_perm, predicate, is_superuser
from rules import is_authenticated, is_active, is_staff


@predicate
def is_requester(user, ticket):
    return user == ticket.requester


@predicate
def is_responder(user, ticket):
    return ticket.is_responder(user)

is_user = is_authenticated & is_active
is_coord = is_user & (is_staff | is_superuser)
is_party = (is_requester | is_responder)

add_perm('ticket.add_ticket', is_user)
add_perm('ticket.view_ticket', is_party)
add_perm('ticket.change_ticket', is_party)
add_perm('ticket.manage_ticket', is_user & is_responder)
add_perm('ticket.join_ticket', is_coord & ~is_requester)
add_perm('ticket.leave_ticket', is_coord)
add_perm('ticket.report_ticket', is_coord)
add_perm('ticket.revoke_ticket', is_user & is_requester)
