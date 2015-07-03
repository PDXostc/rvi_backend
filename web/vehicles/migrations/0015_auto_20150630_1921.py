# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('security', '0004_auto_20150630_1921'),
        ('vehicles', '0014_auto_20150620_0011'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='vehicle',
            name='veh_privkey',
        ),
        migrations.RemoveField(
            model_name='vehicle',
            name='veh_pubkey',
        ),
        migrations.AddField(
            model_name='vehicle',
            name='veh_key',
            field=models.ForeignKey(verbose_name=b'Key', to='security.JSONWebKey', null=True),
            preserve_default=True,
        ),
    ]
