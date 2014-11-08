# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vehicles', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vehicle',
            name='veh_make',
            field=models.CharField(max_length=256, verbose_name=b'Vehicle Make'),
        ),
        migrations.AlterField(
            model_name='vehicle',
            name='veh_model',
            field=models.CharField(max_length=256, verbose_name=b'Vehicle Model'),
        ),
        migrations.AlterField(
            model_name='vehicle',
            name='veh_name',
            field=models.CharField(max_length=256, verbose_name=b'Vehicle Name'),
        ),
        migrations.AlterField(
            model_name='vehicle',
            name='veh_rvibasename',
            field=models.CharField(max_length=256, verbose_name=b'RVI Basename'),
        ),
        migrations.AlterField(
            model_name='vehicle',
            name='veh_vin',
            field=models.CharField(max_length=256, verbose_name=b'Vehicle VIN'),
        ),
        migrations.AlterField(
            model_name='vehicle',
            name='veh_year',
            field=models.CharField(max_length=4, null=True, verbose_name=b'Vehicle Model Year', blank=True),
        ),
    ]
