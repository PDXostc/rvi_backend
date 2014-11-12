# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vehicles', '0003_auto_20141009_2054'),
    ]

    operations = [
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('loc_time', models.DateTimeField(verbose_name=b'Time')),
                ('loc_latitude', models.FloatField(verbose_name=b'Latitude')),
                ('loc_longitude', models.FloatField(verbose_name=b'Longitude')),
                ('loc_altitude', models.FloatField(verbose_name=b'Altitude')),
                ('loc_speed', models.FloatField(verbose_name=b'Speed')),
                ('loc_climb', models.FloatField(verbose_name=b'Climb')),
                ('loc_track', models.FloatField(verbose_name=b'Track')),
                ('loc_vehicle', models.ForeignKey(verbose_name=b'Vehicle', to='vehicles.Vehicle')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
