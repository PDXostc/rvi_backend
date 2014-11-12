# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tracking', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='location',
            name='loc_odometer',
            field=models.FloatField(default=0, verbose_name=b'Odometer'),
            preserve_default=False,
        ),
    ]
