# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vehicles', '0007_auto_20141125_2203'),
    ]

    operations = [
        migrations.AddField(
            model_name='vehicle',
            name='veh_last_altitude',
            field=models.FloatField(default=0, verbose_name=b'Last Altitude [m]'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='vehicle',
            name='veh_last_latitude',
            field=models.FloatField(default=0, verbose_name=b'Last Latitude [deg]'),
        ),
        migrations.AlterField(
            model_name='vehicle',
            name='veh_last_longitude',
            field=models.FloatField(default=0, verbose_name=b'Last Longitude [deg]'),
        ),
    ]
