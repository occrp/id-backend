from django.utils.translation import ugettext_lazy as _

from core.countries import COUNTRIES


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
