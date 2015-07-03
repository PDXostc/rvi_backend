# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('devices', '0002_auto_20150622_2257'),
    ]

    operations = [
        migrations.AlterField(
            model_name='device',
            name='dev_min',
            field=models.CharField(max_length=256, null=True, verbose_name=b'Mobile Identification Number', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='device',
            name='dev_uuid',
            field=models.CharField(default=0, max_length=256, verbose_name=b'UUID'),
            preserve_default=False,
        ),
    ]
