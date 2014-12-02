# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vehicles', '0009_vehicle_veh_picture'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='vehicle',
            name='veh_last_altitude',
        ),
        migrations.RemoveField(
            model_name='vehicle',
            name='veh_last_latitude',
        ),
        migrations.RemoveField(
            model_name='vehicle',
            name='veh_last_longitude',
        ),
        migrations.RemoveField(
            model_name='vehicle',
            name='veh_last_odometer',
        ),
        migrations.RemoveField(
            model_name='vehicle',
            name='veh_last_speed',
        ),
    ]
