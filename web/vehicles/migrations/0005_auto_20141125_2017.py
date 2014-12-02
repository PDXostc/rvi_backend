# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vehicles', '0004_auto_20141125_2007'),
    ]

    operations = [
        migrations.RenameField(
            model_name='vehicle',
            old_name='veh_last_location',
            new_name='geom',
        ),
    ]
