# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import vehicles.models


class Migration(migrations.Migration):

    dependencies = [
        ('vehicles', '0002_auto_20141009_1930'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vehicle',
            name='veh_year',
            field=models.CharField(blank=True, max_length=4, null=True, verbose_name=b'Vehicle Model Year', validators=[vehicles.models.validate_veh_year]),
        ),
    ]
