# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
import ticket.models
from django.conf import settings
import core.mixins


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        # ('podaci', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Budget',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50)),
                ('description', models.TextField(blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Ticket',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('requester_type', models.CharField(default=b'subs', max_length=70, verbose_name='Requester Type', choices=[(b'subs', 'Subsidized'), (b'cost', 'Covering Cost'), (b'cost_plus', 'Covering Cost +')])),
                ('created', models.DateTimeField(default=datetime.datetime.now)),
                ('status', models.CharField(default=b'new', max_length=70, db_index=True, choices=[(b'new', 'New'), (b'in-progress', 'In Progress'), (b'closed', 'Closed'), (b'cancelled', 'Cancelled')])),
                ('status_updated', models.DateTimeField(default=datetime.datetime.now)),
                ('findings_visible', models.BooleanField(default=False, verbose_name='Findings Public')),
                ('is_for_profit', models.BooleanField(default=False, verbose_name='For-Profit?')),
                ('is_public', models.BooleanField(default=False, help_text='Are you okay with the findings becoming public immediately?', verbose_name='Public?')),
                ('user_pays', models.BooleanField(default=True)),
                ('deadline', models.DateField(help_text='How soon do you need this request fulfilled? We will try to meet your deadline, but please note that our researchers are quite busy -- give them as much time as you possibly can!', null=True, verbose_name='Deadline', blank=True)),
                ('sensitive', models.BooleanField(default=False, verbose_name='Sensitive?')),
                ('whysensitive', models.CharField(max_length=150, verbose_name='Why is it sensitive?', blank=True)),
            ],
            options={
            },
            bases=(models.Model, core.mixins.DisplayMixin, core.mixins.NotificationMixin),
        ),
        migrations.CreateModel(
            name='PersonTicket',
            fields=[
                ('ticket_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='ticket.Ticket')),
                ('name', models.CharField(max_length=512, verbose_name='First/other names')),
                ('surname', models.CharField(max_length=100, verbose_name='Last names')),
                ('aliases', models.TextField(help_text='Other names they are known by', verbose_name='Aliases', blank=True)),
                ('dob', models.DateField(null=True, verbose_name='Date of Birth', blank=True)),
                ('background', models.TextField(max_length=300, verbose_name='Your story')),
                ('family', models.TextField(verbose_name='Family and associates', blank=True)),
                ('business_activities', models.TextField(max_length=300, verbose_name='Business Activities')),
                ('initial_information', models.TextField(max_length=150, verbose_name='Where have you looked?')),
            ],
            options={
            },
            bases=('ticket.ticket',),
        ),
        migrations.CreateModel(
            name='OtherTicket',
            fields=[
                ('ticket_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='ticket.Ticket')),
                ('question', models.TextField(verbose_name='What do you want to know?')),
            ],
            options={
            },
            bases=('ticket.ticket',),
        ),
        migrations.CreateModel(
            name='CompanyTicket',
            fields=[
                ('ticket_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='ticket.Ticket')),
                ('name', models.CharField(max_length=512, verbose_name='Company Name')),
                ('country', models.CharField(max_length=100, verbose_name='Country Registered', choices=[(b'', '-----------'), (b'AF', 'Afghanistan'), (b'AX', '\xc5land Islands'), (b'AL', 'Albania'), (b'DZ', 'Algeria'), (b'AS', 'American Samoa'), (b'AD', 'Andorra'), (b'AO', 'Angola'), (b'AI', 'Anguilla'), (b'AQ', 'Antarctica'), (b'AG', 'Antigua and Barbuda'), (b'AR', 'Argentina'), (b'AM', 'Armenia'), (b'AW', 'Aruba'), (b'AU', 'Australia'), (b'AT', 'Austria'), (b'AZ', 'Azerbaijan'), (b'BS', 'Bahamas'), (b'BH', 'Bahrain'), (b'BD', 'Bangladesh'), (b'BB', 'Barbados'), (b'BY', 'Belarus'), (b'BE', 'Belgium'), (b'BZ', 'Belize'), (b'BJ', 'Benin'), (b'BM', 'Bermuda'), (b'BT', 'Bhutan'), (b'BO', 'Bolivia, Plurinational State of'), (b'BQ', 'Bonaire, Sint Eustatius and Saba'), (b'BA', 'Bosnia and Herzegovina'), (b'BW', 'Botswana'), (b'BV', 'Bouvet Island'), (b'BR', 'Brazil'), (b'IO', 'British Indian Ocean Territory'), (b'BN', 'Brunei Darussalam'), (b'BG', 'Bulgaria'), (b'BF', 'Burkina Faso'), (b'BI', 'Burundi'), (b'KH', 'Cambodia'), (b'CM', 'Cameroon'), (b'CA', 'Canada'), (b'CV', 'Cape Verde'), (b'KY', 'Cayman Islands'), (b'CF', 'Central African Republic'), (b'TD', 'Chad'), (b'CL', 'Chile'), (b'CN', 'China'), (b'CX', 'Christmas Island'), (b'CC', 'Cocos (Keeling) Islands'), (b'CO', 'Colombia'), (b'KM', 'Comoros'), (b'CG', 'Congo'), (b'CD', 'Congo, The Democratic Republic of the'), (b'CK', 'Cook Islands'), (b'CR', 'Costa Rica'), (b'CI', "C\xf4te D'ivoire"), (b'HR', 'Croatia'), (b'CU', 'Cuba'), (b'CW', 'Cura\xe7ao'), (b'CY', 'Cyprus'), (b'CZ', 'Czech Republic'), (b'DK', 'Denmark'), (b'DJ', 'Djibouti'), (b'DM', 'Dominica'), (b'DO', 'Dominican Republic'), (b'EC', 'Ecuador'), (b'EG', 'Egypt'), (b'SV', 'El Salvador'), (b'GQ', 'Equatorial Guinea'), (b'ER', 'Eritrea'), (b'EE', 'Estonia'), (b'ET', 'Ethiopia'), (b'FK', 'Falkland Islands (Malvinas)'), (b'FO', 'Faroe Islands'), (b'FJ', 'Fiji'), (b'FI', 'Finland'), (b'FR', 'France'), (b'GF', 'French Guiana'), (b'PF', 'French Polynesia'), (b'TF', 'French Southern Territories'), (b'GA', 'Gabon'), (b'GM', 'Gambia'), (b'GE', 'Georgia'), (b'DE', 'Germany'), (b'GH', 'Ghana'), (b'GI', 'Gibraltar'), (b'GR', 'Greece'), (b'GL', 'Greenland'), (b'GD', 'Grenada'), (b'GP', 'Guadeloupe'), (b'GU', 'Guam'), (b'GT', 'Guatemala'), (b'GG', 'Guernsey'), (b'GN', 'Guinea'), (b'GW', 'Guinea-bissau'), (b'GY', 'Guyana'), (b'HT', 'Haiti'), (b'HM', 'Heard Island and McDonald Islands'), (b'VA', 'Holy See (Vatican City State)'), (b'HN', 'Honduras'), (b'HK', 'Hong Kong'), (b'HU', 'Hungary'), (b'IS', 'Iceland'), (b'IN', 'India'), (b'ID', 'Indonesia'), (b'IR', 'Iran, Islamic Republic of'), (b'IQ', 'Iraq'), (b'IE', 'Ireland'), (b'IM', 'Isle of Man'), (b'IL', 'Israel'), (b'IT', 'Italy'), (b'JM', 'Jamaica'), (b'JP', 'Japan'), (b'JE', 'Jersey'), (b'JO', 'Jordan'), (b'KZ', 'Kazakhstan'), (b'KE', 'Kenya'), (b'KI', 'Kiribati'), (b'KP', "Korea, Democratic People's Republic of"), (b'KR', 'Korea, Republic of'), (b'KW', 'Kuwait'), (b'KG', 'Kyrgyzstan'), (b'KV', 'Republic of Kosovo'), (b'LA', "Lao People's Democratic Republic"), (b'LV', 'Latvia'), (b'LB', 'Lebanon'), (b'LS', 'Lesotho'), (b'LR', 'Liberia'), (b'LY', 'Libya'), (b'LI', 'Liechtenstein'), (b'LT', 'Lithuania'), (b'LU', 'Luxembourg'), (b'MO', 'Macao'), (b'MK', 'Macedonia, The Former Yugoslav Republic of'), (b'MG', 'Madagascar'), (b'MW', 'Malawi'), (b'MY', 'Malaysia'), (b'MV', 'Maldives'), (b'ML', 'Mali'), (b'MT', 'Malta'), (b'MH', 'Marshall Islands'), (b'MQ', 'Martinique'), (b'MR', 'Mauritania'), (b'MU', 'Mauritius'), (b'YT', 'Mayotte'), (b'MX', 'Mexico'), (b'FM', 'Micronesia, Federated States of'), (b'MD', 'Moldova, Republic of'), (b'MC', 'Monaco'), (b'MN', 'Mongolia'), (b'ME', 'Montenegro'), (b'MS', 'Montserrat'), (b'MA', 'Morocco'), (b'MZ', 'Mozambique'), (b'MM', 'Myanmar'), (b'NA', 'Namibia'), (b'NR', 'Nauru'), (b'NP', 'Nepal'), (b'NL', 'Netherlands'), (b'NC', 'New Caledonia'), (b'NZ', 'New Zealand'), (b'NI', 'Nicaragua'), (b'NE', 'Niger'), (b'NG', 'Nigeria'), (b'NU', 'Niue'), (b'NF', 'Norfolk Island'), (b'MP', 'Northern Mariana Islands'), (b'NO', 'Norway'), (b'OM', 'Oman'), (b'PK', 'Pakistan'), (b'PW', 'Palau'), (b'PS', 'Palestinian Territory, Occupied'), (b'PA', 'Panama'), (b'PG', 'Papua New Guinea'), (b'PY', 'Paraguay'), (b'PE', 'Peru'), (b'PH', 'Philippines'), (b'PN', 'Pitcairn'), (b'PL', 'Poland'), (b'PT', 'Portugal'), (b'PR', 'Puerto Rico'), (b'QA', 'Qatar'), (b'RE', 'R\xe9union'), (b'RO', 'Romania'), (b'RU', 'Russian Federation'), (b'RW', 'Rwanda'), (b'BL', 'Saint Barth\xe9lemy'), (b'SH', 'Saint Helena, Ascension and Tristan Da Cunha'), (b'KN', 'Saint Kitts and Nevis'), (b'LC', 'Saint Lucia'), (b'MF', 'Saint Martin (French Part)'), (b'PM', 'Saint Pierre and Miquelon'), (b'VC', 'Saint Vincent and the Grenadines'), (b'WS', 'Samoa'), (b'SM', 'San Marino'), (b'ST', 'Sao Tome and Principe'), (b'SA', 'Saudi Arabia'), (b'SN', 'Senegal'), (b'RS', 'Serbia'), (b'SC', 'Seychelles'), (b'SL', 'Sierra Leone'), (b'SG', 'Singapore'), (b'SX', 'Sint Maarten (Dutch Part)'), (b'SK', 'Slovakia'), (b'SI', 'Slovenia'), (b'SB', 'Solomon Islands'), (b'SO', 'Somalia'), (b'ZA', 'South Africa'), (b'GS', 'South Georgia and the South Sandwich Islands'), (b'SS', 'South Sudan'), (b'ES', 'Spain'), (b'LK', 'Sri Lanka'), (b'SD', 'Sudan'), (b'SR', 'Suriname'), (b'SJ', 'Svalbard and Jan Mayen'), (b'SZ', 'Swaziland'), (b'SE', 'Sweden'), (b'CH', 'Switzerland'), (b'SY', 'Syrian Arab Republic'), (b'TW', 'Taiwan, Province of China'), (b'TJ', 'Tajikistan'), (b'TZ', 'Tanzania, United Republic of'), (b'TH', 'Thailand'), (b'TL', 'Timor-leste'), (b'TG', 'Togo'), (b'TK', 'Tokelau'), (b'TO', 'Tonga'), (b'TT', 'Trinidad and Tobago'), (b'TN', 'Tunisia'), (b'TR', 'Turkey'), (b'TM', 'Turkmenistan'), (b'TC', 'Turks and Caicos Islands'), (b'TV', 'Tuvalu'), (b'UG', 'Uganda'), (b'UA', 'Ukraine'), (b'AE', 'United Arab Emirates'), (b'GB', 'United Kingdom'), (b'US', 'United States'), (b'UM', 'United States Minor Outlying Islands'), (b'UY', 'Uruguay'), (b'UZ', 'Uzbekistan'), (b'VU', 'Vanuatu'), (b'VE', 'Venezuela, Bolivarian Republic of'), (b'VN', 'Viet Nam'), (b'VG', 'Virgin Islands, British'), (b'VI', 'Virgin Islands, U.S.'), (b'WF', 'Wallis and Futuna'), (b'EH', 'Western Sahara'), (b'YE', 'Yemen'), (b'ZM', 'Zambia'), (b'ZW', 'Zimbabwe')])),
                ('background', models.TextField(max_length=300, verbose_name='Your story')),
                ('sources', models.TextField(max_length=150, verbose_name='Where have you looked?')),
                ('connections', models.TextField(verbose_name='Connected People', blank=True)),
            ],
            options={
            },
            bases=('ticket.ticket',),
        ),
        migrations.CreateModel(
            name='TicketCharge',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('item', models.CharField(max_length=64)),
                ('cost', ticket.models.DecimalProperty()),
                ('cost_original_currency', ticket.models.DecimalProperty()),
                ('original_currency', models.CharField(max_length=50)),
                ('reconciled', models.BooleanField(default=False)),
                ('reconciled_date', models.DateTimeField(null=True, blank=True)),
                ('paid_status', models.CharField(default=b'unpaid', max_length=70, choices=[(b'unpaid', 'Unpaid'), (b'paid', 'Paid'), (b'free', 'Paid by OCCRP'), (b'invoiced', 'Invoiced')])),
                ('created', models.DateTimeField(default=datetime.datetime.now)),
                ('budget', models.ForeignKey(blank=True, to='ticket.Budget', null=True)),
                ('ticket', models.ForeignKey(to='ticket.Ticket')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model, core.mixins.DisplayMixin),
        ),
        migrations.CreateModel(
            name='TicketUpdate',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('update_type', models.CharField(default=b'update', max_length=70, choices=[(b'update', 'Updated'), (b'charge', 'Charge Added'), (b'charge_modified', 'Charge Modified'), (b'paid', 'Reconciled Charges'), (b'close', 'Closed'), (b'cancel', 'Cancelled'), (b'reopen', 'Re-Opened'), (b'open', 'Opened'), (b'flag', 'Flagged'), (b'docs_attached', 'Documents Attached'), (b'entities_attached', 'Entities Attached'), (b'comment', 'Comment Added'), (b'join', 'Responder Joined'), (b'leave', 'Responder Left')])),
                ('created', models.DateTimeField(default=datetime.datetime.now)),
                ('comment', models.TextField()),
                ('is_removed', models.BooleanField(default=False)),
                ('author', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
                ('ticket', models.ForeignKey(to='ticket.Ticket')),
            ],
            options={
            },
            bases=(models.Model, core.mixins.NotificationMixin),
        ),
        migrations.AddField(
            model_name='ticket',
            name='files',
            field=models.ManyToManyField(related_name='tickets', to='podaci.PodaciFile'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='ticket',
            name='requester',
            field=models.ForeignKey(related_name='ticket_requests', to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='ticket',
            name='responders',
            field=models.ManyToManyField(related_name='tickets_responded', to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
    ]
