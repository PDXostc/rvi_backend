# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tracking', '0002_location_loc_odometer'),
    ]

    operations = [
        migrations.AlterField(
            model_name='location',
            name='loc_altitude',
            field=models.FloatField(default=0, verbose_name=b'Altitude'),
        ),
        migrations.AlterField(
            model_name='location',
            name='loc_climb',
            field=models.FloatField(default=0, verbose_name=b'Climb'),
        ),
        migrations.AlterField(
            model_name='location',
            name='loc_odometer',
            field=models.FloatField(default=0, verbose_name=b'Odometer'),
        ),
        migrations.AlterField(
            model_name='location',
            name='loc_speed',
            field=models.FloatField(default=0, verbose_name=b'Speed'),
        ),
        migrations.AlterField(
            model_name='location',
            name='loc_track',
            field=models.FloatField(default=0, verbose_name=b'Track'),
        ),
    ]
