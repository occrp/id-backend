#
#  THIS FILE IS OBSOLETE PLEASE SALVAGE ANYTHING USEFUL FROM IT AND KILL IT WITH FIRE
#
from django.utils.translation import ugettext_lazy as _
from id.countries import COUNTRIES, CONTINENTS, REGIONS, CURRENCIES

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


DATABASE_TYPES = (
    ('business', _('Business Registry')),
    ('regional', _('Regional procurement registry')),
    ('regulatory', _('Regulatory Agency')),
    ('commercial', _('Commercial Register')),
    ('court', _('Court Registry')),
    ('gazette', _('Gazette')),
    ('land', _('Land Registry')),
    ('ip', _('Intellectual Property')),
    ('copyright', _('Copyright')),
    ('land_tribunal', _('Land Tribunal')),
    ('maritime', _('Maritime')),
)


DATABASE_COUNTRIES = (
    ('', _('All Databases')),
    ('GLOBAL', _('Global Databases')),
    ('-', '---'),
    ('AFRICA', _('Africa')),
    ('ASIA', _('Asia')),
    ('EUROPE', _('Europe')),
    ('LAMERICA', _('Latin America')),
    ('-', '---'),
) + COUNTRIES[1:]


NOTIFICATION_ACTIONS = (
    (0, _("None")),
    (1, _("Add")),
    (2, _("Edit")),
    (3, _("Delete")),
    (4, _("Update")),
    (5, _("Share")),
    (1000000, _("Other")),
)
NA_NONE = 0
NA_ADD = 1
NA_EDIT = 2
NA_DELETE = 3
NA_UPDATE = 4
NA_SHARE = 5
NA_OTHER = 100

NOTIFICATION_ICONS = (
    (0, 'bell-o'),
    (1, 'plus-square'),
    (2, 'pencil-square'),
    (3, 'minus-square'),
    (4, 'edit'),
    (5, 'share-alt-square'),
    (1000000, 'bomb')
)
