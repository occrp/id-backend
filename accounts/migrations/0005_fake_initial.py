# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
from django.conf import settings
import core.mixins


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0001_initial'),
        ('accounts', '0004_rename_id_profile'),
    ]

    state_operations = [
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(default=django.utils.timezone.now, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('email', models.EmailField(unique=True, max_length=254, verbose_name='E-mail Address')),
                ('user_created', models.DateTimeField(auto_now_add=True)),
                ('profile_updated', models.DateTimeField(auto_now=True)),
                ('last_seen', models.DateTimeField(auto_now=True)),
                ('first_name', models.CharField(max_length=64, verbose_name='First Name')),
                ('last_name', models.CharField(max_length=64, verbose_name='Last Name')),
                ('admin_notes', models.TextField(verbose_name='Admin Notes', blank=True)),
                ('locale', models.CharField(blank=True, max_length=16, choices=[(b'ar', '\u0627\u0644\u0639\u0631\u0628\u064a\u0629'), (b'bg', '\u0411\u044a\u043b\u0433\u0430\u0440\u0441\u043a\u0438'), (b'de', 'Deutsch'), (b'en', 'English'), (b'es', 'Espa\xf1ol'), (b'fr', 'Fran\xe7ais'), (b'hr', 'Hrvatski'), (b'hu', 'Magyar'), (b'mk', '\u041c\u0430\u043a\u0435\u0434\u043e\u043d\u0441\u043a\u0438'), (b'pt', 'Portugu\xeas'), (b'ro', 'Rom\xe2ne\u0219te'), (b'ru', '\u0420\u0443\u0441\u0441\u043a\u0438\u0439'), (b'sl', 'Slovenski'), (b'sq', 'Shqip'), (b'sr', '\u0421\u0440\u043f\u0441\u043a\u0438'), (b'sw', 'Kiswahili'), (b'tr', 'T\xfcrk\xe7e'), (b'uk', '\u0423\u043a\u0440\u0430\u0457\u043d\u0441\u044c\u043a\u0430')])),
                ('requester_type', models.CharField(blank=True, max_length=16, verbose_name='Requester Type', choices=[(b'subs', 'Subsidized'), (b'cost', 'Covering Cost'), (b'cost_plus', 'Covering Cost +')])),
                ('findings_visible', models.BooleanField(default=False, verbose_name='Findings Public')),
                ('is_user', models.BooleanField(default=True, db_index=True)),
                ('is_staff', models.BooleanField(default=False, db_index=True)),
                ('is_volunteer', models.BooleanField(default=False, db_index=True)),
                ('is_active', models.BooleanField(default=True)),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Date Joined')),
                ('phone_number', models.CharField(max_length=24, blank=True)),
                ('organization_membership', models.CharField(max_length=64, blank=True)),
                ('notes', models.TextField(blank=True)),
                ('address', models.CharField(max_length=128, blank=True)),
                ('city', models.CharField(max_length=64, blank=True)),
                ('province', models.CharField(max_length=64, blank=True)),
                ('postal_code', models.CharField(max_length=24, blank=True)),
                ('country', models.CharField(blank=True, max_length=32, choices=[(b'', '-----------'), (b'AF', 'Afghanistan'), (b'AX', '\xc5land Islands'), (b'AL', 'Albania'), (b'DZ', 'Algeria'), (b'AS', 'American Samoa'), (b'AD', 'Andorra'), (b'AO', 'Angola'), (b'AI', 'Anguilla'), (b'AQ', 'Antarctica'), (b'AG', 'Antigua and Barbuda'), (b'AR', 'Argentina'), (b'AM', 'Armenia'), (b'AW', 'Aruba'), (b'AU', 'Australia'), (b'AT', 'Austria'), (b'AZ', 'Azerbaijan'), (b'BS', 'Bahamas'), (b'BH', 'Bahrain'), (b'BD', 'Bangladesh'), (b'BB', 'Barbados'), (b'BY', 'Belarus'), (b'BE', 'Belgium'), (b'BZ', 'Belize'), (b'BJ', 'Benin'), (b'BM', 'Bermuda'), (b'BT', 'Bhutan'), (b'BO', 'Bolivia, Plurinational State of'), (b'BQ', 'Bonaire, Sint Eustatius and Saba'), (b'BA', 'Bosnia and Herzegovina'), (b'BW', 'Botswana'), (b'BV', 'Bouvet Island'), (b'BR', 'Brazil'), (b'IO', 'British Indian Ocean Territory'), (b'BN', 'Brunei Darussalam'), (b'BG', 'Bulgaria'), (b'BF', 'Burkina Faso'), (b'BI', 'Burundi'), (b'KH', 'Cambodia'), (b'CM', 'Cameroon'), (b'CA', 'Canada'), (b'CV', 'Cape Verde'), (b'KY', 'Cayman Islands'), (b'CF', 'Central African Republic'), (b'TD', 'Chad'), (b'CL', 'Chile'), (b'CN', 'China'), (b'CX', 'Christmas Island'), (b'CC', 'Cocos (Keeling) Islands'), (b'CO', 'Colombia'), (b'KM', 'Comoros'), (b'CG', 'Congo'), (b'CD', 'Congo, The Democratic Republic of the'), (b'CK', 'Cook Islands'), (b'CR', 'Costa Rica'), (b'CI', "C\xf4te D'ivoire"), (b'HR', 'Croatia'), (b'CU', 'Cuba'), (b'CW', 'Cura\xe7ao'), (b'CY', 'Cyprus'), (b'CZ', 'Czech Republic'), (b'DK', 'Denmark'), (b'DJ', 'Djibouti'), (b'DM', 'Dominica'), (b'DO', 'Dominican Republic'), (b'EC', 'Ecuador'), (b'EG', 'Egypt'), (b'SV', 'El Salvador'), (b'GQ', 'Equatorial Guinea'), (b'ER', 'Eritrea'), (b'EE', 'Estonia'), (b'ET', 'Ethiopia'), (b'FK', 'Falkland Islands (Malvinas)'), (b'FO', 'Faroe Islands'), (b'FJ', 'Fiji'), (b'FI', 'Finland'), (b'FR', 'France'), (b'GF', 'French Guiana'), (b'PF', 'French Polynesia'), (b'TF', 'French Southern Territories'), (b'GA', 'Gabon'), (b'GM', 'Gambia'), (b'GE', 'Georgia'), (b'DE', 'Germany'), (b'GH', 'Ghana'), (b'GI', 'Gibraltar'), (b'GR', 'Greece'), (b'GL', 'Greenland'), (b'GD', 'Grenada'), (b'GP', 'Guadeloupe'), (b'GU', 'Guam'), (b'GT', 'Guatemala'), (b'GG', 'Guernsey'), (b'GN', 'Guinea'), (b'GW', 'Guinea-bissau'), (b'GY', 'Guyana'), (b'HT', 'Haiti'), (b'HM', 'Heard Island and McDonald Islands'), (b'VA', 'Holy See (Vatican City State)'), (b'HN', 'Honduras'), (b'HK', 'Hong Kong'), (b'HU', 'Hungary'), (b'IS', 'Iceland'), (b'IN', 'India'), (b'ID', 'Indonesia'), (b'IR', 'Iran, Islamic Republic of'), (b'IQ', 'Iraq'), (b'IE', 'Ireland'), (b'IM', 'Isle of Man'), (b'IL', 'Israel'), (b'IT', 'Italy'), (b'JM', 'Jamaica'), (b'JP', 'Japan'), (b'JE', 'Jersey'), (b'JO', 'Jordan'), (b'KZ', 'Kazakhstan'), (b'KE', 'Kenya'), (b'KI', 'Kiribati'), (b'KP', "Korea, Democratic People's Republic of"), (b'KR', 'Korea, Republic of'), (b'KW', 'Kuwait'), (b'KG', 'Kyrgyzstan'), (b'KV', 'Republic of Kosovo'), (b'LA', "Lao People's Democratic Republic"), (b'LV', 'Latvia'), (b'LB', 'Lebanon'), (b'LS', 'Lesotho'), (b'LR', 'Liberia'), (b'LY', 'Libya'), (b'LI', 'Liechtenstein'), (b'LT', 'Lithuania'), (b'LU', 'Luxembourg'), (b'MO', 'Macao'), (b'MK', 'Macedonia, The Former Yugoslav Republic of'), (b'MG', 'Madagascar'), (b'MW', 'Malawi'), (b'MY', 'Malaysia'), (b'MV', 'Maldives'), (b'ML', 'Mali'), (b'MT', 'Malta'), (b'MH', 'Marshall Islands'), (b'MQ', 'Martinique'), (b'MR', 'Mauritania'), (b'MU', 'Mauritius'), (b'YT', 'Mayotte'), (b'MX', 'Mexico'), (b'FM', 'Micronesia, Federated States of'), (b'MD', 'Moldova, Republic of'), (b'MC', 'Monaco'), (b'MN', 'Mongolia'), (b'ME', 'Montenegro'), (b'MS', 'Montserrat'), (b'MA', 'Morocco'), (b'MZ', 'Mozambique'), (b'MM', 'Myanmar'), (b'NA', 'Namibia'), (b'NR', 'Nauru'), (b'NP', 'Nepal'), (b'NL', 'Netherlands'), (b'NC', 'New Caledonia'), (b'NZ', 'New Zealand'), (b'NI', 'Nicaragua'), (b'NE', 'Niger'), (b'NG', 'Nigeria'), (b'NU', 'Niue'), (b'NF', 'Norfolk Island'), (b'MP', 'Northern Mariana Islands'), (b'NO', 'Norway'), (b'OM', 'Oman'), (b'PK', 'Pakistan'), (b'PW', 'Palau'), (b'PS', 'Palestinian Territory, Occupied'), (b'PA', 'Panama'), (b'PG', 'Papua New Guinea'), (b'PY', 'Paraguay'), (b'PE', 'Peru'), (b'PH', 'Philippines'), (b'PN', 'Pitcairn'), (b'PL', 'Poland'), (b'PT', 'Portugal'), (b'PR', 'Puerto Rico'), (b'QA', 'Qatar'), (b'RE', 'R\xe9union'), (b'RO', 'Romania'), (b'RU', 'Russian Federation'), (b'RW', 'Rwanda'), (b'BL', 'Saint Barth\xe9lemy'), (b'SH', 'Saint Helena, Ascension and Tristan Da Cunha'), (b'KN', 'Saint Kitts and Nevis'), (b'LC', 'Saint Lucia'), (b'MF', 'Saint Martin (French Part)'), (b'PM', 'Saint Pierre and Miquelon'), (b'VC', 'Saint Vincent and the Grenadines'), (b'WS', 'Samoa'), (b'SM', 'San Marino'), (b'ST', 'Sao Tome and Principe'), (b'SA', 'Saudi Arabia'), (b'SN', 'Senegal'), (b'RS', 'Serbia'), (b'SC', 'Seychelles'), (b'SL', 'Sierra Leone'), (b'SG', 'Singapore'), (b'SX', 'Sint Maarten (Dutch Part)'), (b'SK', 'Slovakia'), (b'SI', 'Slovenia'), (b'SB', 'Solomon Islands'), (b'SO', 'Somalia'), (b'ZA', 'South Africa'), (b'GS', 'South Georgia and the South Sandwich Islands'), (b'SS', 'South Sudan'), (b'ES', 'Spain'), (b'LK', 'Sri Lanka'), (b'SD', 'Sudan'), (b'SR', 'Suriname'), (b'SJ', 'Svalbard and Jan Mayen'), (b'SZ', 'Swaziland'), (b'SE', 'Sweden'), (b'CH', 'Switzerland'), (b'SY', 'Syrian Arab Republic'), (b'TW', 'Taiwan, Province of China'), (b'TJ', 'Tajikistan'), (b'TZ', 'Tanzania, United Republic of'), (b'TH', 'Thailand'), (b'TL', 'Timor-leste'), (b'TG', 'Togo'), (b'TK', 'Tokelau'), (b'TO', 'Tonga'), (b'TT', 'Trinidad and Tobago'), (b'TN', 'Tunisia'), (b'TR', 'Turkey'), (b'TM', 'Turkmenistan'), (b'TC', 'Turks and Caicos Islands'), (b'TV', 'Tuvalu'), (b'UG', 'Uganda'), (b'UA', 'Ukraine'), (b'AE', 'United Arab Emirates'), (b'GB', 'United Kingdom'), (b'US', 'United States'), (b'UM', 'United States Minor Outlying Islands'), (b'UY', 'Uruguay'), (b'UZ', 'Uzbekistan'), (b'VU', 'Vanuatu'), (b'VE', 'Venezuela, Bolivarian Republic of'), (b'VN', 'Viet Nam'), (b'VG', 'Virgin Islands, British'), (b'VI', 'Virgin Islands, U.S.'), (b'WF', 'Wallis and Futuna'), (b'EH', 'Western Sahara'), (b'YE', 'Yemen'), (b'ZM', 'Zambia'), (b'ZW', 'Zimbabwe')])),
                ('industry', models.CharField(blank=True, max_length=32, choices=[(b'', b'-----------'), (b'non_profit', 'Media: non-profit'), (b'for_profit', 'Media: for-profit'), (b'freelance', 'Media: freelance'), (b'due_diligence', 'Business: due diligence/investigation'), (b'legal', 'Business: legal'), (b'general', 'Business: general'), (b'government', 'Government'), (b'society', 'Civil society/non-profit'), (b'individual', 'Individual'), (b'other', 'Other (please specify)')])),
                ('industry_other', models.CharField(max_length=256, blank=True)),
                ('media', models.CharField(blank=True, max_length=64, choices=[(b'', b'-----------'), (b'website', 'Website'), (b'print', 'Print'), (b'tv', 'Broadcast TV'), (b'radio', 'Broadcast Radio'), (b'other', "Other or don't know")])),
                ('circulation', models.CharField(blank=True, max_length=64, choices=[(b'', b'-----------'), (b'<10k', 'Less than 10,000'), (b'10k-25k', '10,000 to 25,000'), (b'25k-50k', '25,000 to 50,000'), (b'50k-100k', '50,000 to 100,000'), (b'100k-250k', '100,000 to 250,000'), (b'250k-500k', '250,000 to 500,000'), (b'500k+', 'More than 500,000')])),
                ('title', models.CharField(max_length=256, blank=True)),
                ('interests', models.TextField(blank=True)),
                ('expertise', models.TextField(blank=True)),
                ('languages', models.TextField(blank=True)),
                ('availability', models.TextField(blank=True)),
                ('databases', models.TextField(blank=True)),
                ('conflicts', models.TextField(blank=True)),
                ('groups', models.ManyToManyField(related_query_name='user', related_name='user_set', to='auth.Group', blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of his/her group.', verbose_name='groups')),
            ],
            options={
                'abstract': False,
                'verbose_name': 'user',
                'swappable': 'AUTH_USER_MODEL',
                'verbose_name_plural': 'users',
            },
            bases=(core.mixins.NotificationMixin, models.Model),
        ),
        migrations.CreateModel(
            name='AccountRequest',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('request_type', models.CharField(max_length=64, choices=[(b'requester', 'Information Requester'), (b'volunteer', 'Volunteer')])),
                ('approved', models.NullBooleanField(default=None, verbose_name='Approved')),
                ('date_created', models.DateTimeField(auto_now_add=True, verbose_name='Date Created')),
                ('already_updated', models.BooleanField(default=False)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['request_type', 'approved', 'date_created'],
            },
            bases=(models.Model, core.mixins.DisplayMixin),
        ),
        migrations.CreateModel(
            name='Network',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('short_name', models.CharField(max_length=50)),
                ('long_name', models.CharField(max_length=100, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='accountrequest',
            unique_together=set([('user', 'request_type')]),
        ),
        migrations.AddField(
            model_name='profile',
            name='network',
            field=models.ForeignKey(related_name='members', blank=True, to='accounts.Network', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='profile',
            name='user_permissions',
            field=models.ManyToManyField(related_query_name='user', related_name='user_set', to='auth.Permission', blank=True, help_text='Specific permissions for this user.', verbose_name='user permissions'),
            preserve_default=True,
        ),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(state_operations=state_operations)
    ]
