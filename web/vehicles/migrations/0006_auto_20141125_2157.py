# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vehicles', '0005_auto_20141125_2017'),
    ]

    operations = [
        migrations.RenameField(
            model_name='vehicle',
            old_name='geom',
            new_name='veh_geom',
        ),
    ]
