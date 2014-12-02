# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import djgeojson.fields


class Migration(migrations.Migration):

    dependencies = [
        ('vehicles', '0003_auto_20141009_2054'),
    ]

    operations = [
        migrations.AddField(
            model_name='vehicle',
            name='veh_last_location',
            field=djgeojson.fields.PointField(null=True, verbose_name=b'Last Location', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='vehicle',
            name='veh_last_odometer',
            field=models.FloatField(default=0, verbose_name=b'Last Odometer [km]'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='vehicle',
            name='veh_last_speed',
            field=models.FloatField(default=0, verbose_name=b'Last Speed [m/s]'),
            preserve_default=True,
        ),
    ]
