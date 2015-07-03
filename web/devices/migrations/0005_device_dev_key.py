# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('security', '0004_auto_20150630_1921'),
        ('devices', '0004_remove_device_dev_pubkey'),
    ]

    operations = [
        migrations.AddField(
            model_name='device',
            name='dev_key',
            field=models.ForeignKey(verbose_name=b'Key', to='security.JSONWebKey', null=True),
            preserve_default=True,
        ),
    ]
