# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('vehicles', '0013_auto_20150619_1820'),
    ]

    operations = [
        migrations.AddField(
            model_name='vehicle',
            name='veh_privkey',
            field=models.TextField(max_length=9192, null=True, verbose_name=b'Private Key', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='vehicle',
            name='veh_pubkey',
            field=models.TextField(max_length=2048, null=True, verbose_name=b'Public Key', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='vehicle',
            name='account',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
    ]
