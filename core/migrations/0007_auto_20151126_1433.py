# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0006_auto_20151117_0956'),
    ]

    operations = [
        migrations.CreateModel(
            name='AuditLog',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('level', models.IntegerField()),
                ('module', models.CharField(max_length=100)),
                ('filename', models.CharField(max_length=100)),
                ('lineno', models.IntegerField()),
                ('funcname', models.CharField(max_length=100)),
                ('message', models.TextField()),
                ('excinfo', models.TextField()),
                ('exctext', models.TextField()),
                ('process', models.IntegerField()),
                ('thread', models.IntegerField()),
                ('ip', models.IPAddressField(null=True, blank=True)),
                ('timestamp', models.DateTimeField()),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterModelOptions(
            name='notification',
            options={'ordering': ['-timestamp']},
        ),
    ]
