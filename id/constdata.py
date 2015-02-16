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
    ('paid', _('Reconciled Charges')),
    ('close', _('Closed')),
    ('cancel', _('Cancelled')),
    ('reopen', _('Re-Opened')),
    ('open', _('Opened')),
    ('flag', _('Flagged')),
    ('docs_attached', _('Documents Attached')),
    ('entities_attached', _('Entities Attached')),
    ('comment', _('Comment Added'))
)

TICKET_STATUS = (
    ('new', _('New')),
    ('in-progress', _('In Progress')),
    ('closed', _('Closed')),
    ('cancelled', _('Cancelled'))
)

OPEN_TICKET_STATUSES = ['new', 'in-progress']
CLOSED_TICKET_STATUSES = ['closed', 'cancelled']

PAID_STATUS = (
    ('paid', _('Paid')),
    ('free', _('Paid by OCCRP')),
    ('cancelled', _('Cancelled'))
)

RELATIONSHIP_TYPES = {
    'person_person': (
        ('parent', _('Parent')),
        ('spouse', _('Spouse')),
        ('relative', _('Other Relative')),
        ('friend', _('Friend or Acquaintance')),
        ('employer', _('Employer')),
        ('partner', _('Business Partner')),
        ('proxy', _('Proxy')),
    ),
    'person_location': (
        ('birthplace', _('Birthplace')),
        ('registered', _('Registered Address')),
        ('home', _('Home Address')),
    ),
    'company_person': (
        ('director', _('Director')),
        ('secretary', _('Secretary')),
        ('authorized', _('Authorized Person')),
        ('representative', _('Representative')),
        ('shareholder', _('Shareholder')),
        ('employee', _('Employee')),
    ),
    'company_company': (
        ('subsidiary', _('Subsidiary')),
        ('partner', _('Trading Partner')),
        ('director', _('Director')),
        ('secretary', _('Secretary')),
        ('shareholder', _('Shareholder')),
        ),
    'company_location': (
        ('registered', _('Registered Address')),
        ('place', _('Place of Business')),
    ),
    'other': (
        ('other', _('Other')),
    )
}

ALL_RELATIONSHIP_TYPES = [('', '-----------')]
for key, val in RELATIONSHIP_TYPES.iteritems():
    for typ in val:
        ALL_RELATIONSHIP_TYPES.append(typ)

RELATIONSHIP_PRECEDENCE = ['Person', 'Company', 'Location']

INDUSTRY_TYPES = (
    ('', '-----------'),
    ('non_profit', _('Media: non-profit')),
    ('for_profit', _('Media: for-profit')),
    ('freelance', _('Media: freelance')),
    ('due_diligence', _('Business: due diligence/investigation')),
    ('legal', _('Business: legal')),
    ('general', _('Business: general')),
    ('government', _('Government')),
    ('society', _('Civil society/non-profit')),
    ('individual', _('Individual')),
    ('other', _('Other (please specify)'))
)
MEDIA_INDUSTRY_TYPES = ['non_profit', 'for_profit', 'freelance']

ORGANIZATION_TYPES = (
    ('none', _('None')),
    ('occrp', _('OCCRP')),
    ('arij', _('ARIJ')),
    ('ancir', _('ANCIR')),
    ('connectas', _('Connectas in the Americas')),
)

MEDIA_TYPES = (
    ('', '-----------'),
    ('website', _('Website')),
    ('print', _('Print')),
    ('tv', _('Broadcast TV')),
    ('radio', _('Broadcast Radio')),
    ('other', _("Other or don't know")),
)

CIRCULATION_TYPES = (
    ('', '-----------'),
    ('<10k', _('Less than 10,000')),
    ('10k-25k', _('10,000 to 25,000')),
    ('25k-50k', _('25,000 to 50,000')),
    ('50k-100k', _('50,000 to 100,000')),
    ('100k-250k', _('100,000 to 250,000')),
    ('250k-500k', _('250,000 to 500,000')),
    ('500k+', _('More than 500,000')),
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
