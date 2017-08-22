from django.utils.translation import ugettext_lazy as _

from core.countries import COUNTRIES


# FIXME: This is stupid
def get_choice(choice, choices, compare_index=None, return_index=None):
    """
    gettext safe choice getter.

    @param choice: comparator
    @param choices: the list of tuples
    @param compare_index: the index of the tuple that you want to compare
    @param return_index: the index of the tuple that you want value of
    """
    compare_index = 1 if compare_index is None else compare_index
    return_index = 0 if return_index is None else return_index

    if compare_index == 1 and isinstance(choice, basestring):
        choice = _(choice)

    for pair in choices:
        if pair[compare_index] == choice:
            return pair[return_index]

    return None


get_choice_display = lambda c, l: get_choice(c, l,
                                             compare_index=0, return_index=1)

make_choices = lambda l: [v for v, _ in l]


COMPANY_TYPES = (
    ('', '-----------'),
    ('limited', _('Limited liability')),
    ('partnership', _('Partnership')),
    ('stock', _('Stock company')),
    ('foundation', _('Foundation')),
    ('nonprofit', _('Non-profit')),
    ('other', _('Other')),
)

COMPANY_STATUS = (
    ('', '-----------'),
    ('active', _('Active')),
    ('inactive', _('Inactive'))
)

SEX = (
    ('', _('-----------')),
    ('m', _('Male')),
    ('f', _('Female'))
)

REQUESTER_TYPES = (
    ('subs', _('Subsidized')),
    ('cost', _('Covering Cost')),
    ('cost_plus', _('Covering Cost +'))
)

TICKET_TYPES = (
    ('person_ownership', _('Identify what a person owns')),
    ('company_ownership', _('Determine company ownership')),
    ('other', _('Any other question'))
)

TICKET_UPDATE_TYPES = (
    ('update', _('Updated')),
    ('charge', _('Charge Added')),
    ('charge_modified', _('Charge Modified')),
    ('paid', _('Reconciled Charges')),
    ('close', _('Closed')),
    ('cancel', _('Cancelled')),
    ('reopen', _('Re-Opened')),
    ('open', _('Opened')),
    ('flag', _('Flagged')),
    ('docs_attached', _('Documents Attached')),
    ('entities_attached', _('Entities Attached')),
    ('comment', _('Comment Added')),
    ('join', _('Responder Joined')),
    ('leave', _('Responder Left'))
)

TICKET_STATUS = (
    ('new', _('New')),
    ('in-progress', _('In Progress')),
    ('pending', _('Pending')),
    ('closed', _('Closed')),
    ('cancelled', _('Cancelled'))
)

TICKET_STATUS_ICONS = (
    ('new', 'star-o'),
    ('in-progress', 'star-half-o'),
    ('closed', 'star'),
    ('cancelled', 'times')
)

OPEN_TICKET_STATUSES = ['new', 'in-progress']
CLOSED_TICKET_STATUSES = ['closed', 'cancelled']

PAID_STATUS = (
    ('unpaid', _('Unpaid')),
    ('paid', _('Paid')),
    ('free', _('Paid by OCCRP')),
    ('invoiced', _('Invoiced'))
)
