# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vehicles', '0006_auto_20141125_2157'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='vehicle',
            name='veh_geom',
        ),
        migrations.AddField(
            model_name='vehicle',
            name='veh_last_latitude',
            field=models.FloatField(default=0, verbose_name=b'Latitude [deg]'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='vehicle',
            name='veh_last_longitude',
            field=models.FloatField(default=0, verbose_name=b'Longitude [deg]'),
            preserve_default=True,
        ),
    ]
