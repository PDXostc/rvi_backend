# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('devices', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='device',
            name='dev_btmac',
            field=models.CharField(max_length=256, null=True, verbose_name=b'Bluetooth MAC', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='device',
            name='dev_imei',
            field=models.CharField(max_length=256, null=True, verbose_name=b'Mobile Equipment Identifier', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='device',
            name='dev_uuid',
            field=models.CharField(max_length=256, null=True, verbose_name=b'UUID', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='device',
            name='dev_wifimac',
            field=models.CharField(max_length=256, null=True, verbose_name=b'WiFi MAC', blank=True),
            preserve_default=True,
        ),
    ]
