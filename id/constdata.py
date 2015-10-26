#
#  THIS FILE IS OBSOLETE PLEASE SALVAGE ANYTHING USEFUL FROM IT AND KILL IT WITH FIRE
#
from django.utils.translation import ugettext_lazy as _


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


REQUESTER_TYPES = (
    ('subs', _('Subsidized')),
    ('cost', _('Covering Cost')),
    ('cost_plus', _('Covering Cost +'))
)

REQUEST_TYPES = (
    ('requester', _('Information Requester')),
    ('volunteer', _('Volunteer'))
)

NOTIFICATION_ACTIONS = {
    "none": _("None"),
    "add": _("Add"),
    "edit": _("Edit"),
    "delete": _("Delete"),
    "update": _("Update"),
    "share": _("Share"),
    "other": _("Other"),
}

NOTIFICATION_ICONS = {
    "none": 'bell-o',
    "add": 'plus-square',
    "edit": 'pencil-square',
    "delete": 'minus-square',
    "update": 'edit',
    "share": 'share-alt-square',
    "other": 'bomb'
}
