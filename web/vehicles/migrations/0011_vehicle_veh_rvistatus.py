# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vehicles', '0010_auto_20141202_1805'),
    ]

    operations = [
        migrations.AddField(
            model_name='vehicle',
            name='veh_rvistatus',
            field=models.CharField(default=b'OF', max_length=2, verbose_name=b'RVI Status', choices=[(b'OF', b'Offline'), (b'ON', b'Online')]),
            preserve_default=True,
        ),
    ]
