# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vehicles', '0012_vehicle_user'),
    ]

    operations = [
        migrations.RenameField(
            model_name='vehicle',
            old_name='user',
            new_name='account',
        ),
    ]
