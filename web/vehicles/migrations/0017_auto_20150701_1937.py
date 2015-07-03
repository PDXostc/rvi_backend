# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vehicles', '0016_auto_20150630_1937'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vehicle',
            name='veh_rvibasename',
            field=models.CharField(max_length=256, verbose_name=b'RVI Domain'),
            preserve_default=True,
        ),
    ]
