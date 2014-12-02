# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vehicles', '0009_vehicle_veh_picture'),
        ('tracking', '0006_waypoints'),
    ]

    operations = [
        migrations.CreateModel(
            name='Position',
            fields=[
                ('wp_vehicle', models.OneToOneField(primary_key=True, serialize=False, to='vehicles.Vehicle', verbose_name=b'Vehicle')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
