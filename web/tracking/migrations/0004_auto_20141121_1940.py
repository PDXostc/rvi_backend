# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import djgeojson.fields


class Migration(migrations.Migration):

    dependencies = [
        ('tracking', '0003_auto_20141110_2110'),
    ]

    operations = [
        migrations.AddField(
            model_name='location',
            name='geom',
            field=djgeojson.fields.PointField(null=True, verbose_name=b'Geometry', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='location',
            name='loc_altitude',
            field=models.FloatField(default=0, verbose_name=b'Altitude [m]'),
        ),
        migrations.AlterField(
            model_name='location',
            name='loc_climb',
            field=models.FloatField(default=0, verbose_name=b'Climb [m/s]'),
        ),
        migrations.AlterField(
            model_name='location',
            name='loc_latitude',
            field=models.FloatField(verbose_name=b'Latitude [deg]'),
        ),
        migrations.AlterField(
            model_name='location',
            name='loc_longitude',
            field=models.FloatField(verbose_name=b'Longitude [deg]'),
        ),
        migrations.AlterField(
            model_name='location',
            name='loc_odometer',
            field=models.FloatField(default=0, verbose_name=b'Odometer [km]'),
        ),
        migrations.AlterField(
            model_name='location',
            name='loc_speed',
            field=models.FloatField(default=0, verbose_name=b'Speed [m/s]'),
        ),
        migrations.AlterField(
            model_name='location',
            name='loc_track',
            field=models.FloatField(default=0, verbose_name=b'Track [deg]'),
        ),
    ]
