# Generated by Django 3.0.3 on 2020-02-26 14:39

from django.conf import settings
from django.db import migrations, models
from djmoney.models.fields import MoneyField, CurrencyField
from djmoney.settings import CURRENCY_CHOICES


class Migration(migrations.Migration):

    dependencies = [
        ('api_v3', '0012_new_ticket_fields'),
    ]

    operations = [
        migrations.CreateModel(
            name='Expense',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount_currency', CurrencyField(choices=CURRENCY_CHOICES, default='USD', editable=False, max_length=3)),
                ('amount', MoneyField(decimal_places=4, default_currency='USD', max_digits=19, null=True)),
                ('notes', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('ticket', models.ForeignKey(on_delete=models.deletion.DO_NOTHING, related_name='expenses', to='api_v3.Ticket')),
                ('user', models.ForeignKey(on_delete=models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
