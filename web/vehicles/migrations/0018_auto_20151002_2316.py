# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('security', '0010_auto_20151002_2316'),
        ('vehicles', '0017_auto_20150701_1937'),
    ]

    operations = [
        migrations.AddField(
            model_name='vehicle',
            name='canfw_key',
            field=models.OneToOneField(null=True, verbose_name=b'FW_Key', to='security.CANFWKey'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='vehicle',
            name='seq_counter',
            field=models.IntegerField(default=0, verbose_name=b'Sequence Counter', editable=False),
            preserve_default=True,
        ),
    ]
