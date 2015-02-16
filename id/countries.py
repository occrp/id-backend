from django.utils.translation import ugettext_lazy as _
import logging
# pycountry generates many spurious error messages due to duplicate info
# in the underlying database
# see https://bitbucket.org/gocept/pycountry/pull-request/2/added-support-for-former-countries/diff
requests_log = logging.getLogger("pycountry.db")
requests_log.setLevel(logging.WARNING)
import pycountry

skipped_codes = (
    'XXX', 'XTS' #omit some testing currency codes
    )
CURRENCIES = [(x.letter, x.name)
              for x in pycountry.currencies
              if x not in skipped_codes]

COUNTRIES = (
    ('', u'-----------'),
    ('AF', u'Afghanistan'),
    ('AX', u'\xc5land Islands'),
    ('AL', u'Albania'),
    ('DZ', u'Algeria'),
    ('AS', u'American Samoa'),
    ('AD', u'Andorra'),
    ('AO', u'Angola'),
    ('AI', u'Anguilla'),
    ('AQ', u'Antarctica'),
    ('AG', u'Antigua and Barbuda'),
    ('AR', u'Argentina'),
    ('AM', u'Armenia'),
    ('AW', u'Aruba'),
    ('AU', u'Australia'),
    ('AT', u'Austria'),
    ('AZ', u'Azerbaijan'),
    ('BS', u'Bahamas'),
    ('BH', u'Bahrain'),
    ('BD', u'Bangladesh'),
    ('BB', u'Barbados'),
    ('BY', u'Belarus'),
    ('BE', u'Belgium'),
    ('BZ', u'Belize'),
    ('BJ', u'Benin'),
    ('BM', u'Bermuda'),
    ('BT', u'Bhutan'),
    ('BO', u'Bolivia, Plurinational State of'),
    ('BQ', u'Bonaire, Sint Eustatius and Saba'),
    ('BA', u'Bosnia and Herzegovina'),
    ('BW', u'Botswana'),
    ('BV', u'Bouvet Island'),
    ('BR', u'Brazil'),
    ('IO', u'British Indian Ocean Territory'),
    ('BN', u'Brunei Darussalam'),
    ('BG', u'Bulgaria'),
    ('BF', u'Burkina Faso'),
    ('BI', u'Burundi'),
    ('KH', u'Cambodia'),
    ('CM', u'Cameroon'),
    ('CA', u'Canada'),
    ('CV', u'Cape Verde'),
    ('KY', u'Cayman Islands'),
    ('CF', u'Central African Republic'),
    ('TD', u'Chad'),
    ('CL', u'Chile'),
    ('CN', u'China'),
    ('CX', u'Christmas Island'),
    ('CC', u'Cocos (Keeling) Islands'),
    ('CO', u'Colombia'),
    ('KM', u'Comoros'),
    ('CG', u'Congo'),
    ('CD', u'Congo, The Democratic Republic of the'),
    ('CK', u'Cook Islands'),
    ('CR', u'Costa Rica'),
    ('CI', u"C\xf4te D'ivoire"),
    ('HR', u'Croatia'),
    ('CU', u'Cuba'),
    ('CW', u'Cura\xe7ao'),
    ('CY', u'Cyprus'),
    ('CZ', u'Czech Republic'),
    ('DK', u'Denmark'),
    ('DJ', u'Djibouti'),
    ('DM', u'Dominica'),
    ('DO', u'Dominican Republic'),
    ('EC', u'Ecuador'),
    ('EG', u'Egypt'),
    ('SV', u'El Salvador'),
    ('GQ', u'Equatorial Guinea'),
    ('ER', u'Eritrea'),
    ('EE', u'Estonia'),
    ('ET', u'Ethiopia'),
    ('FK', u'Falkland Islands (Malvinas)'),
    ('FO', u'Faroe Islands'),
    ('FJ', u'Fiji'),
    ('FI', u'Finland'),
    ('FR', u'France'),
    ('GF', u'French Guiana'),
    ('PF', u'French Polynesia'),
    ('TF', u'French Southern Territories'),
    ('GA', u'Gabon'),
    ('GM', u'Gambia'),
    ('GE', u'Georgia'),
    ('DE', u'Germany'),
    ('GH', u'Ghana'),
    ('GI', u'Gibraltar'),
    ('GR', u'Greece'),
    ('GL', u'Greenland'),
    ('GD', u'Grenada'),
    ('GP', u'Guadeloupe'),
    ('GU', u'Guam'),
    ('GT', u'Guatemala'),
    ('GG', u'Guernsey'),
    ('GN', u'Guinea'),
    ('GW', u'Guinea-bissau'),
    ('GY', u'Guyana'),
    ('HT', u'Haiti'),
    ('HM', u'Heard Island and McDonald Islands'),
    ('VA', u'Holy See (Vatican City State)'),
    ('HN', u'Honduras'),
    ('HK', u'Hong Kong'),
    ('HU', u'Hungary'),
    ('IS', u'Iceland'),
    ('IN', u'India'),
    ('ID', u'Indonesia'),
    ('IR', u'Iran, Islamic Republic of'),
    ('IQ', u'Iraq'),
    ('IE', u'Ireland'),
    ('IM', u'Isle of Man'),
    ('IL', u'Israel'),
    ('IT', u'Italy'),
    ('JM', u'Jamaica'),
    ('JP', u'Japan'),
    ('JE', u'Jersey'),
    ('JO', u'Jordan'),
    ('KZ', u'Kazakhstan'),
    ('KE', u'Kenya'),
    ('KI', u'Kiribati'),
    ('KP', u"Korea, Democratic People's Republic of"),
    ('KR', u'Korea, Republic of'),
    ('KW', u'Kuwait'),
    ('KG', u'Kyrgyzstan'),
    ('KV', u'Republic of Kosovo'),
    ('LA', u"Lao People's Democratic Republic"),
    ('LV', u'Latvia'),
    ('LB', u'Lebanon'),
    ('LS', u'Lesotho'),
    ('LR', u'Liberia'),
    ('LY', u'Libya'),
    ('LI', u'Liechtenstein'),
    ('LT', u'Lithuania'),
    ('LU', u'Luxembourg'),
    ('MO', u'Macao'),
    ('MK', u'Macedonia, The Former Yugoslav Republic of'),
    ('MG', u'Madagascar'),
    ('MW', u'Malawi'),
    ('MY', u'Malaysia'),
    ('MV', u'Maldives'),
    ('ML', u'Mali'),
    ('MT', u'Malta'),
    ('MH', u'Marshall Islands'),
    ('MQ', u'Martinique'),
    ('MR', u'Mauritania'),
    ('MU', u'Mauritius'),
    ('YT', u'Mayotte'),
    ('MX', u'Mexico'),
    ('FM', u'Micronesia, Federated States of'),
    ('MD', u'Moldova, Republic of'),
    ('MC', u'Monaco'),
    ('MN', u'Mongolia'),
    ('ME', u'Montenegro'),
    ('MS', u'Montserrat'),
    ('MA', u'Morocco'),
    ('MZ', u'Mozambique'),
    ('MM', u'Myanmar'),
    ('NA', u'Namibia'),
    ('NR', u'Nauru'),
    ('NP', u'Nepal'),
    ('NL', u'Netherlands'),
    ('NC', u'New Caledonia'),
    ('NZ', u'New Zealand'),
    ('NI', u'Nicaragua'),
    ('NE', u'Niger'),
    ('NG', u'Nigeria'),
    ('NU', u'Niue'),
    ('NF', u'Norfolk Island'),
    ('MP', u'Northern Mariana Islands'),
    ('NO', u'Norway'),
    ('OM', u'Oman'),
    ('PK', u'Pakistan'),
    ('PW', u'Palau'),
    ('PS', u'Palestinian Territory, Occupied'),
    ('PA', u'Panama'),
    ('PG', u'Papua New Guinea'),
    ('PY', u'Paraguay'),
    ('PE', u'Peru'),
    ('PH', u'Philippines'),
    ('PN', u'Pitcairn'),
    ('PL', u'Poland'),
    ('PT', u'Portugal'),
    ('PR', u'Puerto Rico'),
    ('QA', u'Qatar'),
    ('RE', u'R\xe9union'),
    ('RO', u'Romania'),
    ('RU', u'Russian Federation'),
    ('RW', u'Rwanda'),
    ('BL', u'Saint Barth\xe9lemy'),
    ('SH', u'Saint Helena, Ascension and Tristan Da Cunha'),
    ('KN', u'Saint Kitts and Nevis'),
    ('LC', u'Saint Lucia'),
    ('MF', u'Saint Martin (French Part)'),
    ('PM', u'Saint Pierre and Miquelon'),
    ('VC', u'Saint Vincent and the Grenadines'),
    ('WS', u'Samoa'),
    ('SM', u'San Marino'),
    ('ST', u'Sao Tome and Principe'),
    ('SA', u'Saudi Arabia'),
    ('SN', u'Senegal'),
    ('RS', u'Serbia'),
    ('SC', u'Seychelles'),
    ('SL', u'Sierra Leone'),
    ('SG', u'Singapore'),
    ('SX', u'Sint Maarten (Dutch Part)'),
    ('SK', u'Slovakia'),
    ('SI', u'Slovenia'),
    ('SB', u'Solomon Islands'),
    ('SO', u'Somalia'),
    ('ZA', u'South Africa'),
    ('GS', u'South Georgia and the South Sandwich Islands'),
    ('SS', u'South Sudan'),
    ('ES', u'Spain'),
    ('LK', u'Sri Lanka'),
    ('SD', u'Sudan'),
    ('SR', u'Suriname'),
    ('SJ', u'Svalbard and Jan Mayen'),
    ('SZ', u'Swaziland'),
    ('SE', u'Sweden'),
    ('CH', u'Switzerland'),
    ('SY', u'Syrian Arab Republic'),
    ('TW', u'Taiwan, Province of China'),
    ('TJ', u'Tajikistan'),
    ('TZ', u'Tanzania, United Republic of'),
    ('TH', u'Thailand'),
    ('TL', u'Timor-leste'),
    ('TG', u'Togo'),
    ('TK', u'Tokelau'),
    ('TO', u'Tonga'),
    ('TT', u'Trinidad and Tobago'),
    ('TN', u'Tunisia'),
    ('TR', u'Turkey'),
    ('TM', u'Turkmenistan'),
    ('TC', u'Turks and Caicos Islands'),
    ('TV', u'Tuvalu'),
    ('UG', u'Uganda'),
    ('UA', u'Ukraine'),
    ('AE', u'United Arab Emirates'),
    ('GB', u'United Kingdom'),
    ('US', u'United States'),
    ('UM', u'United States Minor Outlying Islands'),
    ('UY', u'Uruguay'),
    ('UZ', u'Uzbekistan'),
    ('VU', u'Vanuatu'),
    ('VE', u'Venezuela, Bolivarian Republic of'),
    ('VN', u'Viet Nam'),
    ('VG', u'Virgin Islands, British'),
    ('VI', u'Virgin Islands, U.S.'),
    ('WF', u'Wallis and Futuna'),
    ('EH', u'Western Sahara'),
    ('YE', u'Yemen'),
    ('ZM', u'Zambia'),
    ('ZW', u'Zimbabwe'),
)

CONTINENTS = {
    'Europe': set(['', 'BE', 'FR', 'BG', 'DK', 'HR', 'MT', 'BA', 'HU', 'CH', 'FI', 'JE', 'BY', 'GR', 'FO', 'RU', 'NL', 'PT', 'NO', 'LI', 'LV', 'LT', 'LU', 'ES', 'RO', 'PL', 'VA', 'DE', 'AD', 'EE', 'IS', 'AL', 'IT', 'GG', 'CZ', 'IM', 'GB', 'AX', 'IE', 'GI', 'ME', 'MD', 'MC', 'RS', 'MK', 'SK', 'SJ', 'SI', 'SM', 'UA', 'SE', 'AT']),
    'Oceania': set(['WF', 'WS', 'FJ', 'FM', 'PW', 'TV', 'NC', 'NF', 'TO', 'NZ', 'PF', 'TK', 'NR', 'PN', 'NU', 'PG', 'CK', 'GU', 'AS', 'AU', 'VU', 'KI', 'MH', 'MP', 'SB']),
    'Africa': set(['BF', 'DJ', 'BI', 'BJ', 'ZA', 'BW', 'DZ', 'GN', 'YT', 'RW', 'TZ', 'GQ', 'NA', 'NE', 'NG', 'TN', 'RE', 'LR', 'LS', 'TG', 'TD', 'GH', 'LY', 'GW', 'ZM', 'CI', 'EH', 'CM', 'EG', 'SL', 'CG', 'CF', 'AO', 'CD', 'GA', 'ET', 'GM', 'ZW', 'CV', 'ER', 'SZ', 'MG', 'MA', 'KE', 'SS', 'ML', 'KM', 'ST', 'MU', 'MW', 'SH', 'SO', 'SN', 'MR', 'SC', 'UG', 'SD', 'MZ']),
    'Asia': set(['BD', 'KH', 'BN', 'JP', 'BT', 'HK', 'JO', 'PS', 'AZ', 'LB', 'LA', 'TR', 'LK', 'TL', 'TM', 'TJ', 'TH', 'NP', 'PK', 'PH', 'AE', 'CN', 'AF', 'IQ', 'BH', 'IR', 'AM', 'SY', 'VN', 'CY', 'IL', 'IN', 'KP', 'ID', 'OM', 'KG', 'UZ', 'MM', 'SG', 'MO', 'MN', 'GE', 'QA', 'KR', 'MV', 'KW', 'KZ', 'SA', 'MY', 'YE']),
    'Americas': set(['DO', 'CL', 'DM', 'BB', 'BL', 'BM', 'BO', 'HT', 'SV', 'JM', 'GT', 'HN', 'BQ', 'BR', 'BS', 'FK', 'BZ', 'PR', 'NI', 'LC', 'TT', 'GP', 'PA', 'UY', 'PE', 'TC', 'PM', 'VC', 'CO', 'VE', 'AG', 'VG', 'AI', 'VI', 'CA', 'EC', 'GF', 'GD', 'GY', 'AW', 'CR', 'GL', 'CW', 'CU', 'MF', 'SX', 'SR', 'KN', 'US', 'AR', 'MQ', 'PY', 'MS', 'KY', 'MX'])}

REGIONS = {
     'Australia and New Zealand': set(['NZ', 'AU', 'NF']),
     'Caribbean': set(['DO', 'DM', 'BB', 'BL', 'HT', 'JM', 'BQ', 'BS', 'PR', 'LC', 'TT', 'GP', 'TC', 'VC', 'AG', 'VG', 'AI', 'VI', 'GD', 'AW', 'CW', 'CU', 'MF', 'SX', 'KN', 'MQ', 'MS', 'KY']),
     'Central America': set(['NI', 'GT', 'SV', 'PA', 'HN', 'CR', 'MX', 'BZ']),
     'Central Asia': set(['KZ', 'TJ', 'KG', 'TM', 'UZ']),
     'Eastern Africa': set(['ZM', 'MG', 'RW', 'DJ', 'KE', 'BI', 'KM', 'MU', 'RE', 'MW', 'SO', 'TZ', 'ZW', 'SC', 'ET', 'UG', 'MZ', 'YT', 'ER']),
     'Eastern Asia': set(['CN', 'KR', 'MO', 'MN', 'JP', 'HK', 'KP']),
     'Eastern Europe': set(['MD', 'BG', 'RU', 'HU', 'SK', 'CZ', 'RO', 'UA', 'BY', 'PL']),
     'Latin America and the Caribbean': set([]),
     'Melanesia': set(['SB', 'FJ', 'NC', 'PG', 'VU']),
     'Micronesia': set(['GU', 'PW', 'KI', 'MH', 'MP', 'NR', 'FM']),
     'Middle Africa': set(['GQ', 'CM', 'CG', 'CF', 'AO', 'CD', 'GA', 'TD', 'ST']),
     'Northern Africa': set(['MA', 'EH', 'SS', 'EG', 'TN', 'DZ', 'LY', 'SD']),
     'Northern America': set(['BM', 'CA', 'GL', 'US', 'PM']),
     'Northern Europe': set(['', 'LV', 'JE', 'DK', 'NO', 'EE', 'IS', 'GG', 'SJ', 'LT', 'IM', 'GB', 'FI', 'AX', 'IE', 'SE', 'FO']),
     'Polynesia': set(['CK', 'WF', 'TV', 'TO', 'AS', 'PF', 'TK', 'WS', 'PN', 'NU']),
     'South America': set(['PY', 'CO', 'VE', 'CL', 'SR', 'BO', 'EC', 'GF', 'AR', 'GY', 'BR', 'PE', 'UY', 'FK']),
     'South-Eastern Asia': set(['LA', 'MM', 'SG', 'BN', 'KH', 'VN', 'TL', 'TH', 'PH', 'MY', 'ID']),
     'Southern Africa': set(['SZ', 'NA', 'BW', 'LS', 'ZA']),
     'Southern Asia': set(['BD', 'AF', 'IR', 'LK', 'BT', 'MV', 'IN', 'NP', 'PK']),
     'Southern Europe': set(['ME', 'VA', 'GR', 'PT', 'RS', 'HR', 'AL', 'MK', 'IT', 'MT', 'SI', 'ES', 'SM', 'AD', 'GI', 'BA']),
     'Western Africa': set(['GW', 'BF', 'ML', 'SL', 'CI', 'BJ', 'NE', 'TG', 'SH', 'LR', 'SN', 'MR', 'GN', 'GM', 'NG', 'CV', 'GH']),
     'Western Asia': set(['PS', 'OM', 'LB', 'IQ', 'AM', 'TR', 'BH', 'GE', 'SY', 'QA', 'CY', 'JO', 'KW', 'IL', 'AE', 'SA', 'AZ', 'YE']),
     'Western Europe': set(['BE', 'FR', 'CH', 'NL', 'MC', 'DE', 'LI', 'LU', 'AT'])}
