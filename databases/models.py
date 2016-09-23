from django.db import models
from django.utils.translation import ugettext_lazy as _

from core.mixins import DisplayMixin
from core.countries import COUNTRIES

DATABASE_TYPES = (
    ('business', _('Business Registry')),
    ('regional', _('Procurement registry')),
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


EXPAND_REGIONS = {
    'EUROPE': set(['BE', 'FR', 'BG', 'DK', 'HR', 'MT', 'BA', 'HU', 'CH', 'FI', 'JE', 'BY', 'GR', 'FO', 'RU', 'NL', 'PT', 'NO', 'LI', 'LV', 'LT', 'LU', 'ES', 'RO', 'PL', 'VA', 'DE', 'AD', 'EE', 'IS', 'AL', 'IT', 'GG', 'CZ', 'IM', 'GB', 'AX', 'IE', 'GI', 'ME', 'MD', 'MC', 'RS', 'MK', 'SK', 'SJ', 'SI', 'SM', 'UA', 'SE', 'AT']),
    'AFRICA': set(['BF', 'DJ', 'BI', 'BJ', 'ZA', 'BW', 'DZ', 'GN', 'YT', 'RW', 'TZ', 'GQ', 'NA', 'NE', 'NG', 'TN', 'RE', 'LR', 'LS', 'TG', 'TD', 'GH', 'LY', 'GW', 'ZM', 'CI', 'EH', 'CM', 'EG', 'SL', 'CG', 'CF', 'AO', 'CD', 'GA', 'ET', 'GM', 'ZW', 'CV', 'ER', 'SZ', 'MG', 'MA', 'KE', 'SS', 'ML', 'KM', 'ST', 'MU', 'MW', 'SH', 'SO', 'SN', 'MR', 'SC', 'UG', 'SD', 'MZ']),
    'ASIA': set(['BD', 'KH', 'BN', 'JP', 'BT', 'HK', 'JO', 'PS', 'AZ', 'LB', 'LA', 'TR', 'LK', 'TL', 'TM', 'TJ', 'TH', 'NP', 'PK', 'PH', 'AE', 'CN', 'AF', 'IQ', 'BH', 'IR', 'AM', 'SY', 'VN', 'CY', 'IL', 'IN', 'KP', 'ID', 'OM', 'KG', 'UZ', 'MM', 'SG', 'MO', 'MN', 'GE', 'QA', 'KR', 'MV', 'KW', 'KZ', 'SA', 'MY', 'YE']),
    'LAMERICA': set(['DO', 'CL', 'DM', 'BB', 'BL', 'BM', 'BO', 'HT', 'SV', 'JM', 'GT', 'HN', 'BQ', 'BR', 'BS', 'FK', 'BZ', 'PR', 'NI', 'LC', 'TT', 'GP', 'PA', 'UY', 'PE', 'TC', 'PM', 'VC', 'CO', 'VE', 'AG', 'VG', 'AI', 'VI', 'EC', 'GF', 'GD', 'GY', 'AW', 'CR', 'GL', 'CW', 'CU', 'MF', 'SX', 'SR', 'KN', 'AR', 'MQ', 'PY', 'MS', 'KY', 'MX'])}


def get_region(country):
    names = dict(DATABASE_COUNTRIES)
    for region, countries in EXPAND_REGIONS.items():
        if country in countries:
            return names.get(region) + ''


class ExternalDatabase(models.Model, DisplayMixin):
    agency = models.CharField(max_length=500, blank=False,
        verbose_name=_('Agency / Name'))
    db_type = models.CharField(max_length=20, choices=DATABASE_TYPES,
        verbose_name=_('Type of Database'))
    country = models.CharField(max_length=20, choices=DATABASE_COUNTRIES,
        verbose_name=_('Country'))
    paid = models.BooleanField(default=False, verbose_name=_('Paid Database'))
    registration_required = models.BooleanField(default=False,
        verbose_name=_('Registration Required'))
    government_db = models.BooleanField(default=False,
        verbose_name=_('Government Database'))
    url = models.URLField(max_length=2000, blank=False, verbose_name=_('URL'))
    notes = models.TextField(verbose_name=_('Notes'), blank=True)
    blog_post = models.URLField(verbose_name=_('Blog Post'), blank=True)
    video_url = models.URLField(verbose_name=_('YouTube Video Url'), blank=True)

    @property
    def db_type_name(self):
        return dict(DATABASE_TYPES).get(self.db_type) or _('Other registry')

    @property
    def country_name(self):
        return dict(DATABASE_COUNTRIES).get(self.country) or _('No country')

    def __str__(self):
        return self.agency

    def __unicode__(self):
        return unicode(self.agency)
